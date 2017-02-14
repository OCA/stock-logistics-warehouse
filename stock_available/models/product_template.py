# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _product_available(self, name=None, arg=False):
        res = super(ProductTemplate, self)._product_available(name, arg)

        variants = self.env['product.product']
        for product in self:
            variants += product.product_variant_ids
        variant_available = variants._product_available()

        for product in self:
            if isinstance(product.id, models.NewId):
                continue
            immediately_usable_qty = 0.0
            for p in product.product_variant_ids:
                qty = variant_available[p.id]["immediately_usable_qty"]
                immediately_usable_qty += qty
            res[product.id].update({
                "immediately_usable_qty": immediately_usable_qty
            })
        return res

    @api.multi
    @api.depends('product_variant_ids.immediately_usable_qty')
    def _immediately_usable_qty(self):
        """No-op implementation of the stock available to promise.

        By default, available to promise = forecasted quantity.

        **Each** sub-module **must** override this method in **both**
            `product.product` **and** `product.template`, because we can't
            decide in advance how to compute the template's quantity from the
            variants.
        """
        res = self._product_available()
        for tmpl in self.filtered(lambda x: not isinstance(
                x.id, models.NewId)):
            tmpl.immediately_usable_qty = \
                res[tmpl.id]['immediately_usable_qty']

    immediately_usable_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_immediately_usable_qty',
        string='Available to promise',
        help="Stock for this Product that can be safely proposed "
             "for sale to Customers.\n"
             "The definition of this value can be configured to suit "
             "your needs")
