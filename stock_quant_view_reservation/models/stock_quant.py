# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    def action_view_reservations(self):
        self.ensure_one()
        action = self.env.ref("stock.stock_move_line_action").read([])[0]
        action.update(
            {
                "context": {
                    "search_default_location_id": self.location_id.id,
                    "search_default_product_id": self.product_id.id,
                    "search_default_todo": 1,
                },
                "target": "current",
            }
        )
        return action
