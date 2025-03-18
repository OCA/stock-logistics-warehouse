# Copyright 2024 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def action_view_inventory(self):
        action = super().action_view_inventory()
        if "search_default_my_count" in action.get("context", {}):
            del action["context"]["search_default_my_count"]
        return action
