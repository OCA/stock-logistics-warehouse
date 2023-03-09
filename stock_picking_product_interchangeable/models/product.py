from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_tmpl_interchangeable_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_product_tmpl_interchangeable_ids",
        inverse="_inverse_product_tmpl_interchangeable_ids",
    )

    def _compute_product_tmpl_interchangeable_ids(self):
        """Compute interchangeable products"""
        for rec in self:
            rec.product_tmpl_interchangeable_ids = (
                rec.product_variant_ids.product_interchangeable_ids
            )

    def _inverse_product_tmpl_interchangeable_ids(self):
        """Set new interchangeable product"""
        for rec in self:
            rec.product_variant_id.product_replaces_ids = (
                rec.product_tmpl_interchangeable_ids
            )


class Product(models.Model):
    _inherit = "product.product"

    product_interchangeable_ids = fields.Many2many(
        comodel_name="product.product",
        string="Replaces",
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
        string="Replaces",
        relation="product_substitute_rel",
        column1="product_replaced_id",
        column2="product_id",
        help="Products that can substitute current current product",
    )

    def _compute_product_interchangeable_ids(self):
        """Compute interchangeable products"""
        for rec in self:
            rec.product_interchangeable_ids = (
                rec.product_replaces_ids | rec.product_replaced_by_ids
            ) - rec

    def _inverse_product_interchangeable_ids(self):
        """Set new interchangeable product"""
        for rec in self:
            rec.product_replaces_ids = rec.product_interchangeable_ids
