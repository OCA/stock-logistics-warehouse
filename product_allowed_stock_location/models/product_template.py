from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allowed_location_ids = fields.Many2many(
        "stock.location",
        string="Allowed Locations",
        help="Allowed locations for this product",
        domain=[("usage", "=", "internal"), ("active", "=", True)],
    )

    @api.onchange("allowed_location_ids")
    def _onchange_allowed_location_ids(self):
        for template in self:
            if template.product_variant_ids:
                for variant in template.product_variant_ids:
                    variant.allowed_location_ids = template.allowed_location_ids

    def write(self, vals):
        result = super().write(vals)
        if "allowed_location_ids" in vals:
            for template in self:
                for variant in template.product_variant_ids:
                    variant.allowed_location_ids = template.allowed_location_ids
        return result
