from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    inventory_adjustment_id = fields.Many2one("stock.inventory", ondelete="restrict")
