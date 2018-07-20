# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    locked_qty = fields.Float(
        compute='_get_locked_qty',
        type='float',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        string='Blocked',
        help="Quantity of the Lots/Serial Numbers of this Product which are"
             "blocked.")

    @api.multi
    @api.depends('locked_qty')
    def _immediately_usable_qty(self):
        """Subtract quoted quantity from qty available to promise

        This is the same implementation as for variants."""
        super(ProductTemplate, self)._immediately_usable_qty()
        for tmpl in self:
            tmpl.immediately_usable_qty -= tmpl.locked_qty

    @api.multi
    @api.depends('product_variant_ids.locked_qty')
    def _get_locked_qty(self):
        """Compute the quantity using all the variants"""
        for tmpl in self:
            tmpl.locked_qty = sum(
                tmpl.product_variant_ids.mapped("locked_qty"))
