# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockRequestEmployee(TransactionCase):

    def setUp(self):
        super().setUp()
        self.main_company = self.env.ref('base.main_company')
        self.warehouse_id = self.env.ref('stock.warehouse0')
        self.employee_location = self.env.ref(
            'stock_request_employee.location_employee'
        )

        self.product_id = self._create_product('code', 'product')
        self.employee_id = self.env.user.employee_ids[0]
        self.partner_id = self.employee_id.address_home_id

    def _create_product(self, default_code, name, **vals):
        return self.env['product.product'].create(dict(
            name=name,
            default_code=default_code,
            uom_id=self.env.ref('product.product_uom_unit').id,
            type='product',
            **vals
        ))

    def test_stock_request_employee(self):
        expected_date = fields.Datetime.now()
        vals = {
            'company_id': self.main_company.id,
            'requested_by': self.env.user.id,
            'picking_policy': 'direct',
            'expected_date': expected_date,
            'warehouse_id': self.warehouse_id.id,
            'to_employee': False,
            'employee_id': False,
            'stock_request_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'product_uom_qty': 5.0,
                'company_id': self.main_company.id,
                'expected_date': expected_date,
            })]
        }
        order = self.env['stock.request.order'].new(vals)
        order._onchange_to_employee()
        order.stock_request_ids[0]._onchange_to_employee()
        order._onchange_employee()
        order.update({'to_employee': True, 'employee_id': self.employee_id.id})
        order._onchange_to_employee()
        order.stock_request_ids[0]._onchange_to_employee()
        self.assertTrue(order.location_id)
        self.assertTrue(order.stock_request_ids[0])

        order = order.create(order._convert_to_write(order._cache))
        self.assertTrue(order.id)

        order.action_confirm()
        self.assertEqual(order.picking_ids[0].partner_id, self.partner_id)

        self.assertEqual(self.employee_id.stock_order_count, 1)
        self.assertEqual(self.employee_id.stock_request_count, 1)

        res = self.employee_id.action_view_stock_requests()
        self.assertTrue(res['domain'])

        # Check constrains
        with self.assertRaises(ValidationError):
            order.stock_request_ids.write({'to_employee': False})
        with self.assertRaises(ValidationError):
            order.stock_request_ids.write({'employee_id': False})
