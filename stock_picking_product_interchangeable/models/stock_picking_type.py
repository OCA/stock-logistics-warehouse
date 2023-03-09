from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    substitute_products_mode = fields.Selection(
        selection=[("all", "If all available"), ("any", "If any available")],
        string="Substitute Products",
        required=False,
    )
