# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree
from odoo import api, fields, models


class StockRequestOrder(models.Model):

    _inherit = 'stock.request.order'

    to_employee = fields.Boolean(
        help='Set this field to select an employee as Stock Location',
    )
    employee_id = fields.Many2one(
        'hr.employee',
    )

    @api.onchange('employee_id')
    def _onchange_employee(self):
        self.change_childs()

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
        self.change_childs()

    def change_childs(self):
        res = super().change_childs()
        if not self._context.get('no_change_childs', False):
            for line in self.stock_request_ids:
                line.employee_id = self.employee_id
                line.to_employee = self.to_employee
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Add to the existing context of the field `stock_request_ids`
        "employee_id" key for avoiding to be replaced by other view inheritance.
        We have to do this processing in text mode without evaluating context,
        as it can contain JS stuff.
        """
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='stock_request_ids']"):
                node_val = node.get('context', '{}').strip()[1:-1]
                els = node_val.replace(' ', '').split(',') if node_val else []
                els += [
                    "'default_to_employee': to_employee",
                    "'default_employee_id': employee_id"
                ]
                node.set('context', '{' + ', '.join(
                    [el for el in els if len(el) > 0]
                ) + '}')
            res['arch'] = etree.tostring(doc)
        return res
