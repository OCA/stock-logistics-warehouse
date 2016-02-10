# -*- coding: utf-8 -*-
# © 2014 Numérigraphe, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.one
    @api.depends('virtual_available')
    def _immediately_usable_qty(self):
        """Compute the quantity using all the variants"""
        self.immediately_usable_qty = sum(
            [v.immediately_usable_qty for v in self.product_variant_ids])

    immediately_usable_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_immediately_usable_qty',
        string='Available to promise',
        help="Stock for this Product that can be safely proposed "
             "for sale to Customers.\n"
             "The definition of this value can be configured to suit "
             "your needs")
