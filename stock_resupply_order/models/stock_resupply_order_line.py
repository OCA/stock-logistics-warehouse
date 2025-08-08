from odoo import fields, models


class StockResupplyOrderLine(models.Model):
    _name = "stock.resupply.order.line"
    _inherit = ["mail.thread"]
    _description = "A single product quantity for a resupply order"

    stock_resupply_order_id = fields.Many2one(
        "stock.resupply.order",
        ondelete="cascade",
        required=True,
        tracking=True,
    )

    product_id = fields.Many2one("product.product", required=True, tracking=True)

    quantity = fields.Float(required=True, tracking=True)
