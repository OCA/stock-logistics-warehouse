# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.osv import expression


class ProductTemplate(models.Model):

    _inherit = 'product.template'

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
    check_expired_lots = fields.Boolean(
        compute='_compute_check_expired_lots'
    )

    @api.multi
    def _compute_quantities(self):
        res = super(ProductTemplate, self)._compute_quantities()
        for template in self:
            variants = template.product_variant_ids
            template.qty_expired = sum(variants.mapped('qty_expired'))
            template.outgoing_expired_qty = sum(
                variants.mapped('outgoing_expired_qty'))
        return res

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
        quants_removal_domain = expression.OR([
            [('lot_id.removal_date', '=', False)],
            [('lot_id.removal_date', '>', fields.Datetime.now())]
        ])
        lot_domain = expression.AND([
            [('lot_id', '!=', False)],
            quants_removal_domain,
        ])
        lot_domain = expression.OR([
            [('lot_id', '=', False)],
            lot_domain,
        ])
        domain = expression.AND([
            domain,
            lot_domain,
        ])
        action['domain'] = domain
        return action

    @api.multi
    def action_open_expired_quants(self):
        action = super(ProductTemplate, self).action_open_quants()
        domain = action['domain']
        quants_removal_domain = expression.AND([
            [('lot_id.removal_date', '!=', False)],
            [('lot_id.removal_date', '<=', fields.Datetime.now())]
        ])
        lot_domain = expression.AND([
            [('lot_id', '!=', False)],
            quants_removal_domain,
        ])
        domain = expression.AND([
            domain,
            lot_domain,
        ])
        action['domain'] = domain
        return action
