# Copyright 2018-20 ForgeFlow <http://www.forgeflow.com>

from odoo import api, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _get_quants_action(self, domain=None, extend=False):
        action = super()._get_quants_action(domain=domain, extend=extend)
        action["view_id"] = self.env.ref("stock.view_stock_quant_tree").id
        # Enables form view in readonly list
        action.update(
            {
                "view_mode": "tree,form",
                "views": [
                    (action["view_id"], "list"),
                    (self.env.ref("stock.view_stock_quant_form").id, "form"),
                ],
            }
        )
        return action
