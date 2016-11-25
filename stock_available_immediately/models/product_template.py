# -*- coding: utf-8 -*-
# Copyright 2014 Camptocamp, Akretion, Numérigraphe
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    @api.depends('virtual_available', 'incoming_qty')
    def _compute_immediately_usable_qty(self):
        """Ignore the incoming goods in the quantity available to promise

        This is the same implementation as for variants."""
        super(ProductTemplate, self)._compute_immediately_usable_qty()
        for tmpl in self:
            tmpl.immediately_usable_qty -= tmpl.incoming_qty
