# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.misc import format_datetime


class StockQuantityHistory(models.TransientModel):
    _inherit = "stock.quantity.history"

    def open_at_actual_date(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_account.stock_valuation_layer_action"
        )
        action["domain"] = [
            ("actual_date", "<=", self.inventory_datetime),
            ("product_id.type", "=", "product"),
        ]
        action["display_name"] = format_datetime(self.env, self.inventory_datetime)
        return action
