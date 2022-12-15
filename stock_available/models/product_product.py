# Copyright 2014 Numérigraphe
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons.stock.models.product import OPERATORS


class ProductProduct(models.Model):

    """Add a field for the stock available to promise.
    Useful implementations need to be installed through the Settings menu or by
    installing one of the modules stock_available_*
    """

    _inherit = "product.product"

    def _compute_available_quantities_dict(self):
        stock_dict = self._compute_quantities_dict(
            self._context.get("lot_id"),
            self._context.get("owner_id"),
            self._context.get("package_id"),
            self._context.get("from_date"),
            self._context.get("to_date"),
        )
        res = {}
        for product in self:
            res[product.id] = {
                "immediately_usable_qty": stock_dict[product.id]["virtual_available"],
                "potential_qty": 0.0,
            }
        return res, stock_dict

    @api.depends("virtual_available")
    @api.depends_context(
        "lot_id",
        "owner_id",
        "package_id",
        "from_date",
        "to_date",
        "location",
        "warehouse",
    )
    def _compute_available_quantities(self):
        res, _ = self._compute_available_quantities_dict()
        for product in self:
            for key, value in res[product.id].items():
                if hasattr(product, key):
                    product[key] = value

    immediately_usable_qty = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_available_quantities",
        search="_search_immediately_usable_qty",
        string="Available to promise",
        help="Stock for this Product that can be safely proposed "
        "for sale to Customers.\n"
        "The definition of this value can be configured to suit "
        "your needs.",
    )
    potential_qty = fields.Float(
        compute="_compute_available_quantities",
        digits="Product Unit of Measure",
        string="Potential",
        help="Quantity of this Product that could be produced using "
        "the materials already at hand.",
    )

    def _get_search_immediately_usable_qty_domain(self):
        return [("type", "=", "product")]

    @api.model
    def _search_immediately_usable_qty(self, operator, value):
        """Search function for the immediately_usable_qty field.
        The search is quite similar to the Odoo search about quantity available
        (addons/stock/models/product.py,253; _search_product_quantity function)
        :param operator: str
        :param value: str
        :return: list of tuple (domain)
        """
        product_domain = self._get_search_immediately_usable_qty_domain()
        products = self.with_context(prefetch_fields=False).search(
            product_domain, order="id"
        )
        product_ids = []
        for product in products:
            if OPERATORS[operator](product.immediately_usable_qty, value):
                product_ids.append(product.id)
        return [("id", "in", product_ids)]
