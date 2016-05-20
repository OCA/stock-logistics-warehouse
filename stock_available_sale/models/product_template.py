# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    quoted_qty = fields.Float(
        compute='_get_quoted_qty',
        type='float',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        string='Quoted',
        help="Total quantity of this Product that have been included in "
             "Quotations (Draft Sale Orders).\n"
             "In a context with a single Warehouse, this includes "
             "Quotation processed in this Warehouse.\n"
             "In a context with a single Stock Location, this includes "
             "Quotation processed at any Warehouse using "
             "this Location, or any of its children, as it's Stock "
             "Location.\n"
             "Otherwise, this includes every Quotation.")

    @api.multi
    @api.depends('quoted_qty')
    def _immediately_usable_qty(self):
        """Subtract quoted quantity from qty available to promise

        This is the same implementation as for variants."""
        super(ProductTemplate, self)._immediately_usable_qty()
        for tmpl in self:
            tmpl.immediately_usable_qty -= tmpl.quoted_qty

    @api.multi
    @api.depends('product_variant_ids.quoted_qty')
    def _get_quoted_qty(self):
        """Compute the quantity using all the variants"""
        for tmpl in self:
            tmpl.quoted_qty = sum(
                [v.quoted_qty for v in tmpl.product_variant_ids])
