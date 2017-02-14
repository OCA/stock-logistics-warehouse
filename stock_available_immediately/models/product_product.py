# -*- coding: utf-8 -*-
# © 2010-2012 Camptocamp SA
# © 2011 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _product_available(self, field_names=None, arg=False):
        res = super(ProductProduct, self)._product_available(
            field_names=field_names, arg=arg)
        for prod_id in res:
            res[prod_id]['immediately_usable_qty'] = res[prod_id][
                'immediately_usable_qty'] - res[prod_id]['incoming_qty']

        return res

    @api.multi
    @api.depends('virtual_available', 'incoming_qty')
    def _immediately_usable_qty(self):
        """Ignore the incoming goods in the quantity available to promise

        This is the same implementation as for templates."""
        super(ProductProduct, self)._immediately_usable_qty()
