# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class StockMoveReserveAreaLine(models.Model):
    """Will only be created when the move is out of the area"""

    _name = "stock.move.reserve.area.line"
    _description = "Stock Move Reserve Area Line"

    move_id = fields.Many2one("stock.move", index=True, required=True, readonly=True)

    picking_id = fields.Many2one("stock.picking", related="move_id.picking_id")

    reserved_availability = fields.Float(
        string="Reserved in this Area",
        digits="Product Unit of Measure",
        default=0.0,
        readonly=True,
        copy=False,
        help="Quantity that has been reserved in the reserve"
        " Area of the source location.",
    )
    unreserved_qty = fields.Float(
        string="Unreserved Quantity",
        digits="Product Unit of Measure",
        compute="_compute_unreserved_qty",
        store=True,
        readonly=True,
        help="Quantity pending to be reserved in the reserve"
        " Area of the source location.",
    )

    reserve_area_id = fields.Many2one(
        "stock.reserve.area",
        ondelete="cascade",
        index=True,
        required=True,
        readonly=True,
    )

    product_id = fields.Many2one(
        "product.product", related="move_id.product_id", store=True
    )
    not_reserved_in_child_areas = fields.Boolean(
        compute="_compute_not_reserved_in_child_areas",
        search="_search_not_reserved_in_child_areas",
    )

    @api.depends("reserved_availability", "move_id", "move_id.product_uom_qty")
    def _compute_unreserved_qty(self):
        for line in self:
            line.unreserved_qty = (
                line.move_id.product_uom_qty - line.reserved_availability
            )

    def _compute_not_reserved_in_child_areas(self):
        for rec in self:
            # TODO: compute correctly, but in reality we don't need to...
            rec.not_reserved_in_child_areas = True

    def _search_not_reserved_in_child_areas(self, operator, value):
        if operator not in ["=", "!="] or not isinstance(value, bool):
            raise UserError(_("Operation not supported"))
        if operator != "=":
            value = not value
        self._cr.execute(
            """
            SELECT smral1.id, smral1.move_id, smral1.reserve_area_id
            FROM stock_move_reserve_area_line AS smral1
            LEFT JOIN stock_reserve_area_rel AS rel
            ON smral1.reserve_area_id = rel.stock_reserve_area_1
            LEFT JOIN stock_move_reserve_area_line AS smral2
            ON smral2.move_id = smral1.move_id
            AND smral2.reserve_area_id = rel.stock_reserve_area_2
            WHERE coalesce(smral1.reserved_availability,0.0) > 0.0
            AND COALESCE(smral1.reserved_availability, 0.0) >
            COALESCE(smral2.reserved_availability, 0.0)
            GROUP BY smral1.id, smral1.move_id, smral1.reserve_area_id;
        """
        )
        return [
            ("id", "in" if value else "not in", [r[0] for r in self._cr.fetchall()])
        ]

    def name_get(self):
        res = []
        for rec in self:
            name = rec.move_id.display_name
            res.append((rec.id, name))
        return res

    def _action_area_assign(self):
        area_reserved_availability = {
            area_line: area_line.reserved_availability for area_line in self
        }  # reserved in area from this move
        for area_line in self:
            missing_reserved_uom_quantity = (
                area_line.move_id.product_uom_qty
                - area_reserved_availability[area_line]
            )
            missing_reserved_quantity = area_line.move_id.product_uom._compute_quantity(
                missing_reserved_uom_quantity,
                area_line.product_id.uom_id,
                rounding_method="HALF-UP",
            )
            rounding = area_line.product_id.uom_id.rounding
            if float_is_zero(missing_reserved_quantity, precision_rounding=rounding):
                continue
            area_available_quantity = self.env[
                "stock.quant"
            ]._get_reserve_area_available_quantity(
                area_line.product_id, area_line.reserve_area_id
            )
            taken_quantity = min(area_available_quantity, missing_reserved_quantity)
            if float_compare(taken_quantity, 0, precision_rounding=rounding) < 1:
                continue
            area_line.reserved_availability += taken_quantity
