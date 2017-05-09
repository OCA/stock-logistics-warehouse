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
    def _compute_available_quantities_dict(self):
        res = {}
        for product in self:
            res[product.id] = {}
            res[product.id]['immediately_usable_qty'] = \
                product.virtual_available
            res[product.id]['potential_qty'] = 0.0
        return res

    @api.multi
    @api.depends('virtual_available')
    def _compute_available_quantities(self):
        res = self._compute_available_quantities_dict()
        for product in self:
            data = res[product.id]
            for key, value in data.iteritems():
                if hasattr(product, key):
                    product[key] = value

    immediately_usable_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_available_quantities',
        string='Available to promise',
        help="Stock for this Product that can be safely proposed "
             "for sale to Customers.\n"
             "The definition of this value can be configured to suit "
             "your needs")
    potential_qty = fields.Float(
        compute='_compute_available_quantities',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Potential',
        help="Quantity of this Product that could be produced using "
             "the materials already at hand.")
