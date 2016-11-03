# -*- coding: utf-8 -*-
# © 2014 Camptocamp, Akretion, Numérigraphe, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    @api.depends('virtual_available', 'incoming_qty')
    def _compute_immediately_usable_qty(self):
        """Ignore the incoming goods in the quantity available to promise

        This is the same implementation as for templates."""
        super(ProductProduct, self)._compute_immediately_usable_qty()
        for prod in self:
            prod.immediately_usable_qty -= prod.incoming_qty
