# -*- coding: utf-8 -*-
# Copyright 2014 Camptocamp, Akretion, Numérigraphe
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _compute_available_quantities_dict(self):
        res = super(ProductProduct, self)._compute_available_quantities_dict()
        for product in self:
            res[product.id]['immediately_usable_qty'] -= \
                product.incoming_qty
        return res

    @api.depends('virtual_available', 'incoming_qty')
    def _compute_available_quantities(self):
        super(ProductProduct, self)._compute_available_quantities()
