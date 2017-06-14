# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):

    _inherit = 'product.template'

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
    check_expired_lots = fields.Boolean(
        compute='_compute_check_expired_lots'
    )

    @api.multi
    def _compute_expired_qty(self):
        self_with_context = self.with_context(compute_expired_only=True)
        res = self_with_context._compute_quantities_dict()
        for product in self:
            product.qty_expired = res[product.id]['qty_available']
            product.outgoing_expired_qty = res[product.id]['outgoing_qty']

    @api.model
    def _must_check_expired_lots(self):
        param_obj = self.env['ir.config_parameter']
        return param_obj.get_param('stock_qty_available_lot_expired', False)

    @api.multi
    def _compute_check_expired_lots(self):
        check_expired_lots = self._must_check_expired_lots()
        for product in self:
            product.check_expired_lots = check_expired_lots

    @api.multi
    def action_open_quants(self):
        action = super(ProductTemplate, self).action_open_quants()
        domain = action['domain']
        domain += [
            '|',
            ('lot_id', '=', False),
            '&',
            ('lot_id', '!=', False),
            ('lot_id.removal_date', '>', fields.Datetime.now())
        ]
        action['domain'] = domain
        return action

    @api.multi
    def action_open_expired_quants(self):
        action = super(ProductTemplate, self).action_open_quants()
        domain = action['domain']
        domain += [
            ('lot_id', '!=', False),
            ('lot_id.removal_date', '<=', fields.Datetime.now())
        ]
        action['domain'] = domain
        return action
