# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):

    _inherit = 'product.product'

    qty_expired = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_expired_qty',
        string='Expired',
        help="Stock for this Product that must be removed from the stock. "
             "This stock is no more available for sale to Customers.\n"
             "This quantity include all the production lots with a past "
             "removal "
             "date."
    )
    outgoing_expired_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_expired_qty',
        string='Expired Outgoing',
        help="Quantity of products that are planned to leave but which should "
             "be removed from the stock since these are expired."
    )

    def _get_domain_locations(self):
        if not self.env['product.template']._must_check_expired_lots():
            return super(ProductProduct, self)._get_domain_locations()

        quant_domain, move_in_domain, move_out_domain = super(
            ProductProduct, self)._get_domain_locations()

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

        lot_domain = [
            ('lot_id', '!=', False),
            ('lot_id.removal_date', removal_op, max_removal_date)]
        if not compute_expired_only:
            lot_domain = [
                '|',
                ('lot_id', '=', False),
                '&'] + lot_domain

        quant_domain += lot_domain

        return quant_domain, move_in_domain, move_out_domain

    def _get_expired_quants_domain(self, removal_date=None):
        self_with_context = self.with_context(
            compute_expired_only=True, from_date=removal_date)
        return self_with_context._get_domain_locations()[0]

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
