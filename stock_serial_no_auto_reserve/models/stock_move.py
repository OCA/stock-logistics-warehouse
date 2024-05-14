# Copyright 2024 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    is_available = fields.Boolean(
        "Is available but not assigned"
    )

    def _action_assign(self):
        """Dont auto-reserve products with serial number.
        People will have to manually reserve. With regular Odoo
        manual stock.move.line creation this is not possible, people
        will have to use the tag icon from stock_quant_manual_assign"""
        self_auto_reserve = self.filtered(
            lambda m: m.product_id.tracking != "serial"
            or m.product_id.serial_auto_reserve
        )
        self_no_auto_reserve = self - self_auto_reserve
        if self_no_auto_reserve:
            self_no_auto_reserve._update_is_available()
        if self_auto_reserve:
            result = super(
                StockMove, self_auto_reserve.with_context(from_assign=True)
            )._action_assign()
            self_auto_reserve.is_available = False
            return result

    def _update_is_available(self):
        for move in self.filtered(lambda m: m.state in ("waiting", "confirmed")):
            move.is_available = (
                move.forecast_availability == move.product_uom_qty
                and move.reserved_availability < move.product_uom_qty
                and not move.forecast_expected_date
            )
