from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def action_open_quants_show_products(self):
        self.ensure_one()
        return self.product_id.action_open_quants_show_products()
