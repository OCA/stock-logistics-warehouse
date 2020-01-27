# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockRequest(models.Model):

    _inherit = 'stock.request'

    to_employee = fields.Boolean(
        help='Set this field to select an employee as Stock Location',
    )
    employee_id = fields.Many2one(
        'hr.employee',
    )

    @api.onchange('to_employee')
    def _onchange_to_employee(self):
        if self.to_employee:
            self.location_id = self.env.ref(
                'stock_request_employee.location_employee'
            )
            if self.env.user.employee_ids:
                self.employee_id = self.env.user.employee_ids[0]
        else:
            self.employee_id = False
            self.location_id = False

    def _prepare_procurement_values(self, group_id=False):
        res = super()._prepare_procurement_values(group_id)
        if self.to_employee:
            res['partner_id'] = self.employee_id.address_home_id.id or False
        return res

    @api.constrains('order_id', 'to_employee')
    def _check_order_to_employee(self):
        for record in self:
            if (
                record.order_id and
                record.order_id.to_employee != record.to_employee
            ):
                raise ValidationError(_(
                    'To employee flag must be equal to the order'
                ))

    @api.constrains('order_id', 'employee_id')
    def _check_order_employee_id(self):
        for record in self:
            if (
                record.order_id and
                record.order_id.employee_id != record.employee_id
            ):
                raise ValidationError(_(
                    'Employee must be equal to the order'
                ))
