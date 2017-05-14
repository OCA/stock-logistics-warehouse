# -*- coding: utf-8 -*-
# Copyright 2014 Numérigraphe SARL
# Copyright 2016-17 Sodexis, Inc. <dev@sodexis.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    @api.depends('potential_qty')
    def _compute_immediately_usable_qty(self):
        """Add the potential quantity to the quantity available to promise.

        This is the same implementation as for variants."""
        super(ProductTemplate, self)._compute_immediately_usable_qty()
        for tmpl in self:
            tmpl.immediately_usable_qty += tmpl.potential_qty
