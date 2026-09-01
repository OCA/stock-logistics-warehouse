from odoo import fields, models


class Product(models.Model):
    _inherit = "product.product"

    product_interchangeable_ids = fields.Many2many(
        comodel_name="product.product",
        string="Interchangeable Products",
        help="Products that can be substituted by current product",
        inverse="_inverse_product_interchangeable_ids",
        compute="_compute_product_interchangeable_ids",
    )

    product_replaces_ids = fields.Many2many(
        comodel_name="product.product",
        string="Replaces",
        relation="product_substitute_rel",
        column1="product_id",
        column2="product_replaced_id",
        help="Products that can be substituted by current product",
    )
    product_replaced_by_ids = fields.Many2many(
        comodel_name="product.product",
        string="Replaced By",
        relation="product_substitute_rel",
        column1="product_replaced_id",
        column2="product_id",
        help="Products that can substitute current current product",
    )

    def _compute_product_interchangeable_ids(self):
        """Compute interchangeable products"""
        for product_id in self:
            product_id.product_interchangeable_ids = (
                product_id.product_replaces_ids | product_id.product_replaced_by_ids
            ) - product_id

    def _inverse_product_interchangeable_ids(self):
        """Set new interchangeable product"""
        for product_id in self:
            product_id.product_replaces_ids = product_id.product_interchangeable_ids
