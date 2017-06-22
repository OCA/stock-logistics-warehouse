# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import copy
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.osv.expression import is_leaf


class ProductProduct(models.Model):

    _inherit = 'product.product'

    qty_expired = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_quantities',
        string='Expired',
        help="Stock for this Product that must be removed from the stock. "
             "This stock is no more available for sale to Customers.\n"
             "This quantity include all the production lots with a past "
             "removal "
             "date."
    )
    outgoing_expired_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_quantities',
        string='Expired Outgoing',
        help="Quantity of products that are planned to leave but which should "
             "be removed from the stock since these are expired."
    )

    def _get_domain_locations(self):
        quant_domain, move_in_domain, move_out_domain = super(
            ProductProduct, self)._get_domain_locations()
        if self.env['product.template']._must_check_expired_lots():
            quant_domain += self._get_domain_quant_lots()
        return quant_domain, move_in_domain, move_out_domain

    @api.multi
    def _get_domain_quant_lots(self):
        max_removal_date = fields.Datetime.now()
        from_date = self.env.context.get('from_date', False)
        if from_date:
            max_removal_date = from_date
        to_date = self.env.context.get('to_date', False)
        if to_date:
            max_removal_date = to_date

        removal_op = '>'
        compute_expired_only = self.env.context.get('compute_expired_only')
        if compute_expired_only:
            removal_op = '<='

        quants_lot_domain = [
            ('lot_id', '!=', False),
            ('lot_id.removal_date', removal_op, max_removal_date)]
        if not compute_expired_only:
            quants_lot_domain = [
                '|',
                ('lot_id', '=', False),
                '&'] + quants_lot_domain
        return quants_lot_domain

    @api.multi
    def _get_expired_quants_domain(self, removal_date=None):
        """ Compute the domain used to retrieve all the quants in
        stock and reserved for an outgoing move and for an expired stock
        production lot
        :return: quant_domain, quant_out_domain
        """
        from_date = self.env.context.get('from_date', removal_date)
        self_with_context = self.with_context(
            compute_expired_only=True, from_date=from_date)
        quant_domain, move_in_domain, move_out_domain = \
            self_with_context._get_domain_locations()
        quant_out_domain = copy.copy(quant_domain)
        for element in move_out_domain:
            if is_leaf(element):
                quant_out_domain.append(
                    ('reservation_id.' + element[0], element[1], element[2]))
            else:
                quant_out_domain.append(element)

        return quant_domain, quant_out_domain

    @api.multi
    @api.depends('stock_quant_ids', 'stock_move_ids')
    def _compute_quantities(self):
        res = super(ProductProduct, self)._compute_quantities()
        expired_quants_res = self._compute_expired_quants_dict()
        for product in self:
            expired_quantities = expired_quants_res[product.id]
            product.qty_expired = expired_quantities['qty_expired']
            product.outgoing_expired_qty = expired_quantities[
                'outgoing_expired_qty']
            product.outgoing_qty -= product.outgoing_expired_qty
            product.qty_expired -= product.outgoing_expired_qty
        return res

    @api.multi
    def _compute_expired_quants_dict(self):
        quant_domain, quant_out_domain = self._get_expired_quants_domain()
        stock_quant_obj = self.env['stock.quant']
        quants = stock_quant_obj.read_group(
            quant_domain, ['product_id', 'qty'], ['product_id'])
        quant_res = {
            item['product_id'][0]: item['qty'] for item in quants}
        quants_out = stock_quant_obj.read_group(
            quant_out_domain, ['product_id', 'qty'], ['product_id'])
        quant_out_res = {
            item['product_id'][0]: item['qty'] for item in quants_out}
        res = dict()
        for product in self.with_context(prefetch_fields=False):
            quantities = {}
            res[product.id] = quantities
            quantities['outgoing_expired_qty'] = float_round(
                quant_out_res.get(product.id, 0.0),
                precision_rounding=product.uom_id.rounding
            )
            quantities['qty_expired'] = float_round(
                quant_res.get(product.id, 0.0),
                precision_rounding=product.uom_id.rounding
            )
        return res

    @api.multi
    def _compute_expired_qty(self):
        self_with_context = self.with_context(compute_expired_only=True)
        res = self_with_context._product_available()
        for product in self:
            product.qty_expired = res[product.id]['qty_available']
            product.outgoing_expired_qty = res[product.id]['outgoing_qty']

    @api.multi
    def action_open_expired_quants(self):
        action = self.env.ref('stock.product_open_quants').read()[0]
        domain = [
            ('product_id', 'in', self.ids),
            ('lot_id', '!=', False),
            ('lot_id.removal_date', '<=', fields.Datetime.now())
        ]
        action['domain'] = domain
        return action
