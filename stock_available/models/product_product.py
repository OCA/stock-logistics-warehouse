# -*- coding: utf-8 -*-
# Copyright 2014 Numérigraphe
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):

    """Add a field for the stock available to promise.
    Useful implementations need to be installed through the Settings menu or by
    installing one of the modules stock_available_*
    """
    _inherit = 'product.product'

    @api.multi
    def _product_available(self, field_names=None, arg=False):
        res = super(ProductProduct, self)._product_available(
            field_names=field_names, arg=arg)
        for prod_id in res:
            res[prod_id]['immediately_usable_qty'] = res[prod_id][
                'virtual_available']
            res[prod_id]['potential_qty'] = 0.0

        return res

    @api.multi
    @api.depends('virtual_available')
    def _compute_immediately_usable_qty(self):
        """No-op implementation of the stock available to promise.

        By default, available to promise = forecasted quantity.

        **Each** sub-module **must** override this method in **both**
            `product.product` **and** `product.template`, because we can't
            decide in advance how to compute the template's quantity from the
            variants.
        """
        res = self._product_available()
        for prod in self:
            prod.immediately_usable_qty = res[prod.id][
                'immediately_usable_qty']

    @api.multi
    @api.depends()
    def _compute_potential_qty(self):
        """Set potential qty to 0.0 to define the field defintion used by
        other modules to inherit it
        """
        res = self._product_available()
        for prod in self:
            prod.immediately_usable_qty = res[prod.id][
                'potential_qty']

    immediately_usable_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_immediately_usable_qty',
        string='Available to promise',
        help="Stock for this Product that can be safely proposed "
             "for sale to Customers.\n"
             "The definition of this value can be configured to suit "
             "your needs")
    potential_qty = fields.Float(
        compute='_compute_potential_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Potential',
        help="Quantity of this Product that could be produced using "
             "the materials already at hand.")
