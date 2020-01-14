# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    stock_request_ids = fields.One2many(
        'stock.request',
        inverse_name='employee_id',
        readonly=True,
    )
    stock_request_count = fields.Integer(
        compute='_compute_stock_request_count'
    )
    stock_order_ids = fields.One2many(
        'stock.request.order',
        inverse_name='employee_id',
        readonly=True,
    )
    stock_order_count = fields.Integer(
        compute='_compute_stock_order_count'
    )

    @api.depends('stock_order_ids')
    def _compute_stock_order_count(self):
        for record in self:
            record.stock_order_count = len(record.stock_order_ids)

    @api.depends('stock_request_ids')
    def _compute_stock_request_count(self):
        for record in self:
            record.stock_request_count = len(record.stock_request_ids)

    @api.multi
    def action_view_stock_requests(self):
        action = self.env.ref('stock_request.action_stock_request_form')
        result = action.read()[0]
        result['domain'] = [('employee_id', '=', self.id)]
        return result
