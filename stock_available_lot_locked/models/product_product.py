# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

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
        """Subtract the blocked quantity from the qty available to promise.

        This is the same implementation as for templates."""
        super(ProductProduct, self)._immediately_usable_qty()
        for product in self:
            product.immediately_usable_qty -= product.locked_qty

    @api.multi
    def _get_locked_qty(self):
        """Compute the total qty of blocked lots."""
        # Domain of the quants of locked lots
        domain_quant = [('product_id', 'in', self.ids), ('locked', '=', True)]
        # Restrict to the requested locations, lot, owner, package
        domain_quant += self._get_domain_locations()[0]
        if self.env.context.get('lot_id'):
            domain_quant.append(
                ('lot_id', '=', self.env.context['lot_id']))
        if self.env.context.get('owner_id'):
            domain_quant.append(
                ('owner_id', '=', self.env.context['owner_id']))
        if self.env.context.get('package_id'):
            domain_quant.append(
                ('package_id', '=', self.env.context['package_id']))

        quants = self.env['stock.quant'].read_group(
            domain_quant, ['product_id', 'qty'], ['product_id'])
        for quant in quants:
            product = self.browse(quant['product_id'][0])
            product.locked_qty = quant['qty']
