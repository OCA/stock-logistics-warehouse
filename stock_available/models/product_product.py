# Copyright 2014 Numérigraphe
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
import operator as py_operator

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}


class ProductProduct(models.Model):

    """ Add a field for the stock available to promise.
    Useful implementations need to be installed through the Settings menu or by
    installing one of the modules stock_available_*
    """
    _inherit = 'product.product'

    @api.multi
    def _compute_available_quantities_dict(self):
        res = {}
        for product in self:
            res[product.id] = {
                'immediately_usable_qty': product.virtual_available,
                'potential_qty': 0.0
            }
        return res

    @api.multi
    @api.depends('virtual_available')
    def _compute_available_quantities(self):
        res = self._compute_available_quantities_dict()
        for product in self:
            for key, value in res[product.id].items():
                if hasattr(product, key):
                    product[key] = value

    immediately_usable_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_available_quantities',
        search="_search_immediately_usable_qty",
        string='Available to promise',
        help="Stock for this Product that can be safely proposed "
             "for sale to Customers.\n"
             "The definition of this value can be configured to suit "
             "your needs.")
    potential_qty = fields.Float(
        compute='_compute_available_quantities',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Potential',
        help="Quantity of this Product that could be produced using "
             "the materials already at hand.")

    @api.model
    def _search_immediately_usable_qty(self, operator, value):
        """ Search function for the immediately_usable_qty field.
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
        return [('id', 'in', product_ids)]
