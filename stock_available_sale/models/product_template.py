# -*- coding: utf-8 -*-
# Copyright 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    quoted_qty = fields.Float(
        compute='_compute_quoted_qty',
        type='float',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Quoted',
        help="Total quantity of this Product that have been included in "
             "Quotations (Draft Sale Orders).\n"
             "In a context with a single Warehouse, this includes "
             "Quotation processed in this Warehouse.\n"
             "In a context with a single Stock Location, this includes "
             "Quotation processed at any Warehouse using "
             "this Location, or any of its children, as it's Stock "
             "Location.\n"
             "Otherwise, this includes every Quotation.",
    )

    @api.depends('product_variant_ids.quoted_qty')
    def _compute_quoted_qty(self):
        """Compute the quantity using all the variants"""
        for tmpl in self:
            tmpl.quoted_qty = sum(
                tmpl.product_variant_ids.mapped('quoted_qty'))
