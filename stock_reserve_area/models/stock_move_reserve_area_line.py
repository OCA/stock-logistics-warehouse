# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockMoveReserveAreaLine(models.Model):
    """Will only be created when the move is out of the area"""

    _name = "stock.move.reserve.area.line"

    move_id = fields.Many2one("stock.move", index=True)

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

    reserve_area_id = fields.Many2one(
        "stock.reserve.area", ondelete="cascade", index=True
    )

    product_id = fields.Many2one(
        "product.product", related="move_id.product_id", store=True
    )
    not_reserved_in_child_areas = fields.Boolean(
        compute="_compute_not_reserved_in_child_areas",
        search="_search_not_reserved_in_child_areas",
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

    def _action_area_assign(self):
        area_reserved_availability = {
            area_line: area_line.reserved_availability for area_line in self
        }  # reserved in area from this move
        for area_line in self:
            area_available_quantity = self.env[
                "stock.quant"
            ]._get_reserve_area_available_quantity(
                area_line.product_id, area_line.reserve_area_id
            )
            missing_reserved_uom_quantity = (
                area_line.move_id.product_uom_qty
                - area_reserved_availability[area_line]
            )
            missing_reserved_quantity = area_line.move_id.product_uom._compute_quantity(
                missing_reserved_uom_quantity,
                area_line.product_id.uom_id,
                rounding_method="HALF-UP",
            )
            need = missing_reserved_quantity
            if area_available_quantity <= 0:
                continue
            taken_quantity = min(area_available_quantity, need)
            rounding = area_line.product_id.uom_id.rounding
            if float_is_zero(taken_quantity, precision_rounding=rounding):
                continue
            area_line.reserved_availability += taken_quantity
