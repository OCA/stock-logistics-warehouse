# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockReserveArea(models.Model):
    _name = "stock.reserve.area"

    name = fields.Char()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )

    location_ids = fields.Many2many(
        "stock.location",
        relation="stock_reserve_area_stock_location_rel",
        column1="reserve_area_id",
        column2="location_id",
        help="Selected locations a and their children will belong to the Reserve Area",
        domain="""[
        ('usage', 'in', ('internal', 'view')),
        ('company_id', '=', company_id)
        ]""",
    )
    child_area_ids = fields.Many2many(
        comodel_name="stock.reserve.area",
        relation="stock_reserve_area_rel",
        column1="stock_reserve_area_1",
        column2="stock_reserve_area_2",
        compute="_compute_child_area_ids",
        store=True,
    )

    @api.depends("location_ids")
    def _compute_child_area_ids(self):
        computed_areas = self.env.context.get(
            "computed_areas", self.env["stock.reserve.area"]
        )
        child_areas = self.env["stock.reserve.area"]
        for area in self:
            if isinstance(area.id, models.NewId):
                continue
            location_areas = area.location_ids.mapped("reserve_area_ids") - area
            for location_area in location_areas:
                if all(
                    area.is_location_in_area(loc) for loc in location_area.location_ids
                ):
                    # All the locations in the location area are inside of our area.
                    # Therefore this is a child area.
                    child_areas |= location_area
            area.child_area_ids = child_areas
            computed_areas |= area
            if computed_areas:
                location_areas = location_areas - computed_areas
            location_areas.with_context(
                computed_areas=computed_areas
            )._compute_child_area_ids()

    @api.constrains("location_ids")
    def check_location_ids(self):
        # allareas have to be concentric areas.
        areas = self.location_ids.mapped(
            "reserve_area_ids"
        )  # areas that contain this area's locations
        for (
            area
        ) in areas:  # we loop through all areas to verify that they are concentric
            loc_areas = (
                area.location_ids.mapped("reserve_area_ids") - area
            )  # we check consistency for all areas of each location
            for loc_area in loc_areas:
                # or all loc_area locations are inside area or all area locations are
                # inside loc_area
                if not all(
                    area.is_location_in_area(loc) for loc in loc_area.location_ids
                ) and not all(
                    loc_area.is_location_in_area(loc) for loc in area.location_ids
                ):
                    raise UserError(_("All Areas must be concentric"))

    def is_location_in_area(self, location):
        return bool(location in self.location_ids)

    @api.onchange("location_ids")
    def _onchange_location_ids(self):
        # we add all child locations in the reserve area
        self.location_ids = self.env["stock.location"].search(
            [("id", "child_of", self.location_ids.ids)]
        )

    def update_reserve_area_lines(self, moves, locs_to_add, locs_to_delete):
        if self.env.context.get("init_hook", False):
            return
        for move in moves:
            reserve_area_line = self.env["stock.move.reserve.area.line"].search(
                [("move_id", "=", move.id), ("reserve_area_id", "=", self.id)]
            )
            if (
                move._is_out_area(self)
                and not reserve_area_line
                and (
                    move.location_id in locs_to_add
                    or move.location_dest_id in locs_to_delete
                )
            ):
                # the move was within the same area but we removed dest location from it
                # and now is out move the move didn't impact this area but now the
                # source location is inside of it and it's out move
                move.reserve_area_ids |= self
                if move.state not in ("confirmed", "waiting"):
                    # TODO don't unreserve and reserve, reserve in area the locally reserved qty
                    move._do_unreserve()
                    move._action_assign()  # will create new reserve_area_line and reserve
            elif not move._is_out_area(self) and (
                move.location_dest_id in locs_to_add
                or move.location_id in locs_to_delete
            ):
                # 1. the move was out of the area but we dest loc is added in area so it
                # is not out move anymore.
                # 2. the move was out of the area but we remove source location from
                # area so this area doesn't apply for reservation.
                move.reserve_area_ids -= self
                if reserve_area_line:
                    # TODO don't unreserve and reserve, recalculate area_reserved_availability
                    reserve_area_line.unlink()
                    move._do_unreserve()
                    move._action_assign()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        moves_impacted = self.env["stock.move"].search(
            [
                ("location_id", "in", res.location_ids.ids),
                ("location_dest_id", "not in", res.location_ids.ids),
                (
                    "state",
                    "in",
                    ("confirmed", "waiting", "assigned", "partially_available"),
                ),
            ]
        )
        res.update_reserve_area_lines(moves_impacted, res.location_ids, [])
        return res

    def write(self, vals):
        location_ids = self.location_ids
        res = super().write(vals)
        if vals.get("location_ids"):
            to_write = self.env["stock.location"].browse(
                x for x in vals.get("location_ids")[0][2]
            )
            to_delete = location_ids - to_write
            to_add = to_write - location_ids
            moves_impacted = self.env["stock.move"].search(
                [
                    "|",
                    ("location_id", "in", to_add.ids + to_delete.ids),
                    ("location_dest_id", "in", to_add.ids + to_delete.ids),
                    (
                        "state",
                        "in",
                        ("confirmed", "waiting", "partially_available", "assigned"),
                    ),
                ]
            )
            self.update_reserve_area_lines(moves_impacted, to_add, to_delete)
        return res

    def unlink(self):
        locations = self.location_ids
        res = super().unlink()
        moves_impacted = self.env["stock.move"].search(
            [
                ("location_id", "in", locations.ids),
                (
                    "state",
                    "in",
                    ("confirmed", "waiting", "partially_available", "assigned"),
                ),
            ]
        )
        moves_impacted._compute_area_reserved_availability()
        return res

    def action_open_reserved_moves(self):
        self.ensure_one()
        move_reserve_area_lines = self.env["stock.move.reserve.area.line"].search(
            [("reserve_area_id", "=", self.id), ("reserved_availability", "!=", 0)]
        )
        view_id = self.env.ref("stock_reserve_area.move_reserve_area_line_tree").id
        context = dict(self.env.context or {})
        context["search_default_group_product_id"] = 1
        return {
            "name": _("Reserved in Areas lines"),
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": "stock.move.reserve.area.line",
            "view_id": view_id,
            "target": "new",
            "search_view_id": self.env.ref(
                "stock_reserve_area.move_reserve_area_line_search"
            ).id,
            "domain": [("id", "in", move_reserve_area_lines.ids)],
            "context": context,
        }
