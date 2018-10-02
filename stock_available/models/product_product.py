# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp
from openerp.tools.safe_eval import safe_eval


class ProductProduct(models.Model):
    """Add a field for the stock available to promise.
    Useful implementations need to be installed through the Settings menu or by
    installing one of the modules stock_available_*
    """
    _inherit = 'product.product'

    @api.multi
    @api.depends('virtual_available')
    def _immediately_usable_qty(self):
        """No-op implementation of the stock available to promise.

        By default, available to promise = forecasted quantity.

        **Each** sub-module **must** override this method in **both**
            `product.product` **and** `product.template`, because we can't
            decide in advance how to compute the template's quantity from the
            variants.
        """
        for prod in self:
            prod.immediately_usable_qty = prod.virtual_available

    def _search_immediately_usable_quantity(self, operator, value):
        res = []
        assert operator in (
            '<', '>', '=', '!=', '<=', '>='
        ), 'Invalid domain operator'
        assert isinstance(
            value, (float, int)
        ), 'Invalid domain value'
        if operator == '=':
            operator = '=='

        ids = []
        products = self.search([])
        for prod in products:
            expr = str(prod.immediately_usable_qty) + operator + str(value)
            eval_dict = {'prod': prod, 'operator': operator, 'value': value}
            if safe_eval(expr, eval_dict):
                ids.append(prod.id)
        res.append(('id', 'in', ids))
        return res

    immediately_usable_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_immediately_usable_qty',
        search='_search_immediately_usable_quantity',
        string='Available to promise',
        help="Stock for this Product that can be safely proposed "
             "for sale to Customers.\n"
             "The definition of this value can be configured to suit "
             "your needs")
