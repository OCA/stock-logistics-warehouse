# -*- coding: utf-8 -*-
# © 2014 Numérigraphe, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


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

    immediately_usable_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_immediately_usable_qty',
        string='Available to promise',
        help="Stock for this Product that can be safely proposed "
             "for sale to Customers.\n"
             "The definition of this value can be configured to suit "
             "your needs")
