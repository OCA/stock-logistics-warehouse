# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import ValidationError

from .product_product import MSG_ERROR_HAS_STOCK


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def write(self, vals):
        if "active" in vals.keys() and not vals["active"]:
            self._check_has_quantities()
        return super().write(vals)

    def _check_has_quantities(self):
        quantities = self.sudo().product_variant_ids._check_has_quantities_archive()
        if quantities:
            raise ValidationError(
                MSG_ERROR_HAS_STOCK
                + self.sudo().product_variant_ids._format_errors_archive(quantities)
            )
