from odoo import fields, models


class TestProductQtyByPackagingMixin(models.Model):
    _name = "test.product.qty_by_packaging.mixin"
    _description = "Test ProductQtyByPackagingMixin"
    _inherit = ["product.qty_by_packaging.mixin"]
    _qty_by_pkg__qty_field_name = "quantity"

    product_id = fields.Many2one("product.product")
    quantity = fields.Float()
