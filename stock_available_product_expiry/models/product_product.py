# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import copy
from contextlib import contextmanager
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.osv import expression


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

    def _get_original_domain_locations(self):
        """ Allow to get domains without the filter on the
        expired lots
        """
        return self.with_context(
            disable_check_expired_lots=True)._get_domain_locations()

    def _get_domain_locations(self):
        quant_domain, move_in_domain, move_out_domain = super(
            ProductProduct, self)._get_domain_locations()
        if (not self.env.context.get('disable_check_expired_lots', False) and
                self.env['product.template']._must_check_expired_lots()):
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

        lot_domain = expression.AND([
            [('lot_id', '!=', False)],
            [('lot_id.removal_date', '!=', False)]
        ])

        quants_lot_domain = expression.AND([
            lot_domain,
            [('lot_id.removal_date', removal_op, max_removal_date)],
        ])
        if not compute_expired_only:
            removal_unset_domain = expression.OR([
                [('lot_id', '=', False)],
                [('lot_id.removal_date', '=', False)]
            ])
            quants_lot_domain = expression.OR([
                removal_unset_domain,
                quants_lot_domain,
            ])
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
            if expression.is_leaf(element):
                quant_out_domain.append(
                    ('reservation_id.' + element[0], element[1], element[2]))
            else:
                quant_out_domain.append(element)
        if self:
            quant_domain = expression.AND([
                [('product_id', 'in', self.ids)],
                quant_domain
                ])
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
            if not self.env.context.get('disable_check_expired_lots', False):
                # We let this to have possibility to get standard quantity
                product.outgoing_qty -= product.outgoing_expired_qty
            product.qty_expired -= product.outgoing_expired_qty
        return res

    @api.model
    @contextmanager
    def _force_auto_join(self, model_field_list):
        """ Force  auto_join for each item (model_name, field_name)
        in model_field_list
        The original value are restored on exit
        """
        vals = {}
        for model_name, field_name in model_field_list:
            field = self.env[model_name]._fields[field_name]
            vals[field] = field.auto_join
            field.auto_join = True
        try:
            yield
        finally:
            for field, value in vals.iteritems():
                field.auto_join = value

    def _get_quants(self, quant_domain, quant_out_domain):
        # Get auto_join value and reset them after read groups
        # This to improve performances without breaking normal behaviour
        stock_quant_obj = self.env['stock.quant']
        with self._force_auto_join([
            ('stock.quant', 'lot_id'),
                ('stock.quant', 'reservation_id')]):
            quants = stock_quant_obj.with_context(lang='').read_group(
                quant_domain, ['product_id', 'qty'], ['product_id'])
            quants_out = stock_quant_obj.with_context(lang='').read_group(
                quant_out_domain, ['product_id', 'qty'], ['product_id'])
            return quants, quants_out

    @api.multi
    def _compute_expired_quants_dict(self):
        quant_domain, quant_out_domain = self._get_expired_quants_domain()
        quants, quants_out = self._get_quants(quant_domain, quant_out_domain)
        quant_res = {
            item['product_id'][0]: item['qty'] for item in quants}
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
    def action_open_expired_quants(self):
        action = self.env.ref('stock.product_open_quants').read()[0]
        quants_removal_domain = expression.OR([
            [('lot_id.removal_date', '=', False)],
            [('lot_id.removal_date', '<=', fields.Datetime.now())]
        ])
        lot_domain = expression.AND([
            [('product_id', 'in', self.ids)],
            [('lot_id', '!=', False)]
        ])
        domain = expression.AND([
            lot_domain,
            quants_removal_domain,
        ])
        action['domain'] = domain
        return action
