# Copyright 2014 Numérigraphe
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons.stock.models.product import OPERATORS


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends(
        "product_variant_ids.immediately_usable_qty",
        "product_variant_ids.potential_qty",
    )
    def _compute_available_quantities(self):
        res = self._compute_available_quantities_dict()
        for product in self:
            for key, value in res[product.id].items():
                if key in product._fields:
                    product[key] = value

    def _compute_available_quantities_dict(self):
        variants_dict, _ = self.mapped(
            "product_variant_ids"
        )._compute_available_quantities_dict()
        res = {}
        for template in self:
            immediately_usable_qty = sum(
                [
                    variants_dict[p.id]["immediately_usable_qty"]
                    - variants_dict[p.id]["potential_qty"]
                    for p in template.product_variant_ids
                ]
            )
            potential_qty = max(
                [
                    variants_dict[p.id]["potential_qty"]
                    for p in template.product_variant_ids
                ]
                or [0.0]
            )
            res[template.id] = {
                "immediately_usable_qty": immediately_usable_qty + potential_qty,
                "potential_qty": potential_qty,
            }
        return res

    immediately_usable_qty = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_available_quantities",
        search="_search_immediately_usable_qty",
        string="Available to promise",
        help="Stock for this Product that can be safely proposed "
        "for sale to Customers.\n"
        "The definition of this value can be configured to suit "
        "your needs",
    )
    potential_qty = fields.Float(
        compute="_compute_available_quantities",
        digits="Product Unit of Measure",
        string="Potential",
        help="Quantity of this Product that could be produced using "
        "the materials already at hand. "
        "If the product has several variants, this will be the biggest "
        "quantity that can be made for a any single variant.",
    )

    @api.model
    def _search_immediately_usable_qty(self, operator, value):
        """Search function for the immediately_usable_qty field.
        The search is quite similar to the Odoo search about quantity available
        (addons/stock/models/product.py,253; _search_product_quantity function)
        :param operator: str
        :param value: str
        :return: list of tuple (domain)
        """
        products = self.search([])
        # Force prefetch
        products.mapped("immediately_usable_qty")
        product_ids = []
        for product in products:
            if OPERATORS[operator](product.immediately_usable_qty, value):
                product_ids.append(product.id)
        return [("id", "in", product_ids)]
