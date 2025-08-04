from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    allowed_location_ids = fields.Many2many(
        "stock.location",
        string="Allowed Locations",
        help="Allowed locations for this product",
    )
