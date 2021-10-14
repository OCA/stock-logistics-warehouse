# Copyright 20121 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def _run_fifo(self, quantity, company):
        vals = super(Product, self)._run_fifo(quantity, company)
        phantom_boms = (
            self.env["mrp.bom.line"]
            .search(
                [
                    ("product_id", "in", self.ids),
                    ("bom_id.type", "=", "phantom"),
                    "|",
                    ("company_id", "=", company.id),
                    ("company_id", "=", False),
                ]
            )
            .mapped("bom_id")
        )
        products = phantom_boms.mapped("product_id")
        products |= phantom_boms.mapped("product_tmpl_id.product_variant_ids")
        for product in products:
            ph_boms = phantom_boms.filtered(
                lambda b: b.product_id == product) or phantom_boms.filtered(
                lambda b: b.product_tmpl_id == product.product_tmpl_id)
            if ph_boms:
                cost = product._compute_bom_price(ph_boms[0], boms_to_recompute=[])
                product.sudo().with_context(force_company=company.id).standard_price = cost
        return vals
