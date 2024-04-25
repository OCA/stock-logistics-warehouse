# Copyright 2024 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        """Dont auto-reserve products with serial number.
        People will have to manually reserve. With regular Odoo
        manual stock.move.line creation this is not possible, people
        will have to use the tag icon from stock_quant_manual_assign"""
        self_not_serial = self.filtered(
            lambda m: m.product_id.tracking != "serial"
            or m.product_id.serial_auto_reserve
        )
        if self_not_serial:
            return super(
                StockMove, self_not_serial.with_context(from_assign=True)
            )._action_assign()
