# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools import OrderedSet, float_compare, float_is_zero, float_round


class StockMove(models.Model):
    _inherit = "stock.move"

    reserve_area_line_ids = fields.One2many("stock.move.reserve.area.line", "move_id")
    reserve_area_ids = fields.Many2many(
        "stock.reserve.area", compute="_compute_reserve_area_ids", store=True
    )
    area_reserved_availability = fields.Float(
        string="Reserved in Area",
        digits="Product Unit of Measure",
        readonly=True,
        copy=False,
        help="Quantity that has been reserved in all reserve"
        " Areas of the source location.",
        compute="_compute_area_reserved_availability",  # minimum of area's reserved
        store=True,
    )

    @api.depends("reserve_area_line_ids.reserved_availability")
    def _compute_area_reserved_availability(self):
        for move in self:
            if move.reserve_area_line_ids:
                move.area_reserved_availability = min(
                    move.reserve_area_line_ids.mapped("reserved_availability")
                )
            else:
                move.area_reserved_availability = 0

    @api.depends("location_id")
    def _compute_reserve_area_ids(self):
        loc_to_area_map = dict()
        for location in self.mapped("location_id"):
            reserve_areas = self.env["stock.reserve.area"].search([])
            for reserve_area in reserve_areas:
                if reserve_area.is_location_in_area(location):
                    if not loc_to_area_map.get(location.id):
                        loc_to_area_map[location.id] = reserve_area
                    else:
                        loc_to_area_map[location.id] |= reserve_area
        for move in self:
            move.reserve_area_ids = loc_to_area_map.get(move.location_id.id)

    def _is_out_area(self, reserve_area_id):
        # out of area = true if source location in area and dest location outside
        for move in self:
            if not reserve_area_id.is_location_in_area(
                move.location_dest_id
            ) and reserve_area_id.is_location_in_area(move.location_id):
                return True
            return False

    def create_reserve_area_lines(self):
        line_ids = self.reserve_area_line_ids
        for reserve_area in self.reserve_area_ids:
            if self._is_out_area(reserve_area) and not self.env[
                "stock.move.reserve.area.line"
            ].search(
                [("move_id", "=", self.id), ("reserve_area_id", "=", reserve_area.id)]
            ):
                line_ids += self.env["stock.move.reserve.area.line"].create(
                    {
                        "move_id": self.id,
                        "reserve_area_id": reserve_area.id,
                    }
                )
        return line_ids

    def _action_area_assign(self):
        for move in self.filtered(
            lambda m: m.state in ["confirmed", "waiting", "partially_available"]
            and m.reserve_area_line_ids
        ):
            move.reserve_area_line_ids._action_area_assign()

    def _action_assign(self):
        for move in self.filtered(
            lambda m: m.state in ["confirmed", "waiting", "partially_available"]
        ):
            move.reserve_area_line_ids = move.create_reserve_area_lines()
        self._action_area_assign()  # new method to assign globally
        super()._action_assign()

    def _get_available_quantity(
        self,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
        allow_negative=False,
    ):
        local_available = super()._get_available_quantity(
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
            allow_negative=allow_negative,
        )
        if self.reserve_area_line_ids:
            return min(local_available, self.area_reserved_availability)
        return local_available

    def _do_area_unreserve(self):
        # we will delete area_reserve_line_ids from the elegible moves
        moves_to_unreserve = OrderedSet()
        for move in self:
            if (
                move.state == "cancel"
                or (move.state == "done" and move.scrapped)
                or not move.reserve_area_line_ids
            ):
                # We may have cancelled move in an open picking in a
                # "propagate_cancel" scenario.
                # We may have done move in an open picking in a scrap scenario.
                continue
            moves_to_unreserve.add(move.id)
        self.env["stock.move"].browse(moves_to_unreserve).mapped(
            "reserve_area_line_ids"
        ).unlink()

    def _do_unreserve(self):
        super()._do_unreserve()
        self._do_area_unreserve()
        return True

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder)
        res.reserve_area_line_ids.unlink()
        return res

    def _free_reservation_area(self, product_id, reserve_area_id, quantity):
        area_available_quantity = self.env[
            "stock.quant"
        ]._get_reserve_area_available_quantity(product_id, reserve_area_id)
        if quantity > area_available_quantity:
            outdated_move_domain = [
                ("state", "not in", ["done", "cancel"]),
                ("product_id", "=", product_id.id),
                ("reserve_area_ids", "in", reserve_area_id.id),
            ]
            # We take the pickings with the latest scheduled date
            outdated_candidates = (
                self.env["stock.move"]
                .search(outdated_move_domain)
                .sorted(
                    lambda cand: (
                        -cand.picking_id.scheduled_date.timestamp()
                        if cand.picking_id
                        else -cand.id,
                    )
                )
            )
            # As the move's state is not computed over the move lines, we'll have to manually
            # recompute the moves which we adapted their lines.
            move_to_recompute_state = self

            for candidate in outdated_candidates:
                rounding = candidate.product_uom.rounding
                quantity_uom = product_id.uom_id._compute_quantity(
                    quantity, candidate.product_uom, rounding_method="HALF-UP"
                )
                reserve_area_line = self.env["stock.move.reserve.area.line"].search(
                    [
                        ("move_id", "=", candidate.id),
                        ("reserve_area_id", "=", reserve_area_id.id),
                        ("reserved_availability", ">", 0.0),
                    ]
                )
                if reserve_area_line:
                    if (
                        float_compare(
                            reserve_area_line.reserved_availability,
                            quantity_uom,
                            precision_rounding=rounding,
                        )
                        <= 0
                    ):
                        quantity_uom -= reserve_area_line.reserved_availability
                        reserve_area_line.reserved_availability = 0
                        move_to_recompute_state |= candidate
                        if float_is_zero(quantity_uom, precision_rounding=rounding):
                            break
                    else:
                        # split this move line and assign the new part to our extra move
                        quantity_left = float_round(
                            reserve_area_line.reserved_availability - quantity_uom,
                            precision_rounding=rounding,
                            rounding_method="UP",
                        )
                        reserve_area_line.reserved_availability = quantity_left
                        move_to_recompute_state |= candidate
                    # cover case where units have been removed from the area and then a
                    # move has reserved locally but not in area
                    if (
                        float_compare(
                            candidate.area_reserved_availability,
                            candidate.reserved_availability,
                            precision_rounding=rounding,
                        )
                        < 0
                    ):
                        to_remove = float_round(
                            candidate.reserved_availability
                            - candidate.area_reserved_availability,
                            precision_rounding=rounding,
                            rounding_method="UP",
                        )
                        # treiem les quants d'algun move line
                        mls = candidate.move_line_ids
                        removed = 0
                        for ml in mls:
                            while removed < to_remove:
                                ml_removed = min(ml.product_uom_qty, to_remove)
                                ml.product_uom_qty -= ml_removed
                                removed += ml_removed
                        break
            move_to_recompute_state._recompute_state()
