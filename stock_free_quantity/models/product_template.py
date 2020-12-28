# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _compute_quantities_dict(self):
        prod_available = super()._compute_quantities_dict()
        for template in self:
            free_qty = 0
            for p in template.with_context(active_test=False).product_variant_ids:
                free_qty += p.free_qty
            prod_available[template.id]["free_qty"] = free_qty
        return prod_available

    def _compute_quantities(self):
        super()._compute_quantities()
        res = self._compute_quantities_dict()
        for template in self:
            template.free_qty = res[template.id]["free_qty"]

    def _search_free_qty(self, operator, value):
        return [("product_variant_ids.free_qty", operator, value)]

    free_qty = fields.Float(
        "Free Quantity",
        compute="_compute_quantities",
        search="_search_free_qty",
        compute_sudo=False,
        digits="Product Unit of Measure",
    )
