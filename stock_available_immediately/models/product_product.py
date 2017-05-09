# -*- coding: utf-8 -*-
# Copyright 2014 Camptocamp, Akretion, Numérigraphe
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _product_available(self, field_names=None, arg=False):
        res = super(ProductProduct, self)._product_available(
            field_names=field_names, arg=arg)
        for prod_id in res:
            res[prod_id]['immediately_usable_qty'] =\
                res[prod_id]['immediately_usable_qty'] - \
                res[prod_id]['incoming_qty']

        return res
