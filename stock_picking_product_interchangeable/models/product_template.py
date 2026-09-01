from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_tmpl_interchangeable_ids = fields.Many2many(
        "product.product",
        compute="_compute_product_tmpl_interchangeable_ids",
        inverse="_inverse_product_tmpl_interchangeable_ids",
    )

    def _compute_product_tmpl_interchangeable_ids(self):
        """Compute interchangeable products."""
        for product_id in self:
            product_id.product_tmpl_interchangeable_ids = (
                product_id.product_variant_ids.product_interchangeable_ids
            )

    def _inverse_product_tmpl_interchangeable_ids(self):
        """Set new interchangeable product."""
        for product_id in self:
            product_id.product_variant_id.product_replaces_ids = (
                product_id.product_tmpl_interchangeable_ids
            )
