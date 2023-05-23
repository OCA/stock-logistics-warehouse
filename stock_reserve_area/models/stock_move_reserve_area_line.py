# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_is_zero


class StockMoveReserveAreaLine(models.Model):
    """Will only be created when the move is out of the area"""

    _name = "stock.move.reserve.area.line"

    move_id = fields.Many2one("stock.move")

    picking_id = fields.Many2one("stock.picking", related="move_id.picking_id")

    reserved_availability = fields.Float(
        string="Reserved in this Area",
        digits="Product Unit of Measure",
        readonly=True,
        copy=False,
        help="Quantity that has been reserved in the reserve"
        " Area of the source location.",
    )

    reserve_area_id = fields.Many2one("stock.reserve.area", ondelete="cascade")

    product_id = fields.Many2one(
        "product.product", related="move_id.product_id", store=True
    )

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
