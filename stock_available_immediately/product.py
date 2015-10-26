# -*- coding: utf-8 -*-
# © 2014 Camptocamp, Akretion, Numérigraphe, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class Product(models.Model):
    """Subtract incoming qty from immediately_usable_qty"""
    _inherit = 'product.product'

    @api.multi
    @api.depends('virtual_available', 'incoming_qty')
    def _immediately_usable_qty(self):
        """Ignore the incoming goods in the quantity available to promise"""
        super(ProductProduct, self)._immediately_usable_qty()
        for prod in self:
            prod.immediately_usable_qty -= prod.incoming_qty
