# -*- coding: utf-8 -*-
# © 2014 Camptocamp, Akretion, Numérigraphe, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.one
    def _immediately_usable_qty(self):
        """Ignore the incoming goods in the quantity available to promise"""
        super(ProductProduct, self)._immediately_usable_qty()
        self.immediately_usable_qty -= self.incoming_qty
