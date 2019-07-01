# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    purchase_ids = fields.One2many('purchase.order',
                                   compute='_compute_purchase_ids',
                                   string='Purchase Orders', readonly=True)
    purchase_count = fields.Integer(string='Purchase count',
                                    compute='_compute_purchase_ids',
                                    readonly=True)
    purchase_line_ids = fields.Many2many('purchase.order.line',
                                         compute='_compute_purchase_ids',
                                         string='Purchase Order Lines',
                                         readonly=True, copy=False)

    @api.depends('stock_request_ids')
    def _compute_purchase_ids(self):
        for req in self.sudo():
            req.purchase_ids = req.stock_request_ids.mapped('purchase_ids')
            req.purchase_line_ids = req.stock_request_ids.mapped(
                'purchase_line_ids')
            req.purchase_count = len(req.purchase_ids)

    @api.multi
    def action_view_purchase(self):
        action = self.env.ref(
            'purchase.purchase_order_action_generic').read()[0]
        purchases = self.mapped('purchase_ids')
        if len(purchases) > 1:
            action['domain'] = [('id', 'in', purchases.ids)]
        elif purchases:
            action['views'] = [
                (self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = purchases.id
        return action
