# -*- coding: utf-8 -*-
# © 2015 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    @api.depends('virtual_available', 'incoming_qty')
    def _immediately_usable_qty(self):
        """Ignore the incoming goods in the quantity available to promise

        This is the same implementation as for variants."""
        super(ProductTemplate, self)._immediately_usable_qty()
        for tmpl in self:
            tmpl.immediately_usable_qty -= tmpl.incoming_qty
