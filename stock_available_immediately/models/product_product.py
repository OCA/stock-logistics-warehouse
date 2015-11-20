# -*- coding: utf-8 -*-
# © 2010-2012 Camptocamp SA
# © 2011 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    @api.depends('virtual_available', 'incoming_qty')
    def _immediately_usable_qty(self):
        """Ignore the incoming goods in the quantity available to promise

        This is the same implementation as for templates."""
        super(ProductProduct, self)._immediately_usable_qty()
        for prod in self:
            prod.immediately_usable_qty -= prod.incoming_qty
