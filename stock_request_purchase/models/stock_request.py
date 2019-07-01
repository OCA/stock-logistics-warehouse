# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockRequest(models.Model):
    _inherit = "stock.request"

    purchase_ids = fields.One2many('purchase.order',
                                   compute='_compute_purchase_ids',
                                   string='Purchase Orders', readonly=True)
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

    @api.constrains('purchase_line_ids', 'company_id')
    def _check_purchase_company_constrains(self):
        if any(any(line.company_id != req.company_id for
                   line in req.purchase_line_ids) for req in self):
            raise ValidationError(
                _('You have linked to a purchase order line '
                  'that belongs to another company.'))

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
