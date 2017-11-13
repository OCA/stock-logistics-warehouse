# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequest(models.Model):
    _inherit = "stock.request"

    purchase_ids = fields.One2many('purchase.order',
                                   compute='_compute_purchase_ids',
                                   string='Pickings', readonly=True)
    purchase_count = fields.Integer(string='Purchase count',
                                    compute='_compute_purchase_ids',
                                    readonly=True)
    purchase_line_ids = fields.Many2many('purchase.order.line',
                                         string='Purchase Order Lines',
                                         readonly=True, copy=False)

    @api.depends('purchase_line_ids')
    def _compute_purchase_ids(self):
        for request in self.sudo():
            request.purchase_ids = request.purchase_line_ids.mapped('order_id')
            request.purchase_count = len(request.purchase_ids)

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
