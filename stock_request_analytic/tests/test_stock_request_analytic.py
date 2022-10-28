# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.stock_request.tests import test_stock_request
from odoo import fields
from odoo.exceptions import ValidationError


class TestStockRequestAnalytic(test_stock_request.TestStockRequest):
    def setUp(self):
        super(TestStockRequestAnalytic, self).setUp()
        self.analytic_model = self.env['account.analytic.account']
        self.analytic = self.analytic_model.create({'name': 'Pizza'})
        self.analytic2 = self.analytic_model.create(
            {'name': 'Pizza',
             'company_id': self.company_2.id})
        self.demand_loc = self.env['stock.location'].create(
            {'name': 'demand_loc',
             'location_id': self.warehouse.lot_stock_id.id,
             'usage': 'internal'})
        self.demand_route = self.env['stock.location.route'].create({
            'name': 'Transfer',
            'product_categ_selectable': False,
            'product_selectable': True,
            'company_id': self.main_company.id,
            'sequence': 10,
        })
        self.pizza = self._create_product('PZ', 'Pizza', False)
        self.demand_rule = self.env['procurement.rule'].create({
            'name': 'Transfer',
            'route_id': self.demand_route.id,
            'location_src_id': self.warehouse.lot_stock_id.id,
            'location_id': self.demand_loc.id,
            'action': 'move',
            'picking_type_id': self.warehouse.int_type_id.id,
            'procure_method': 'make_to_stock',
            'warehouse_id': self.warehouse.id,
            'company_id': self.main_company.id,
            'propagate': 'False',
        })
        self.pizza.route_ids = [(6, 0, self.demand_route.ids)]

    def prepare_order_request_analytic(self, aa, company):
        expected_date = fields.Datetime.now()
        vals = {
            'company_id': company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.demand_loc.id,
            'expected_date': expected_date,
            'stock_request_ids': [(0, 0, {
                'product_id': self.pizza.id,
                'product_uom_id': self.pizza.uom_id.id,
                'product_uom_qty': 5.0,
                'analytic_account_id': aa.id,
                'company_id': company.id,
                'warehouse_id': self.warehouse.id,
                'location_id': self.demand_loc.id,
                'expected_date': expected_date,
            })]
        }
        return vals

    def test_stock_analytic(self):
        vals = self.prepare_order_request_analytic(
            self.analytic, self.main_company)
        order = self.env['stock.request.order'].create(vals)
        req = order.stock_request_ids
        order.action_confirm()
        self.assertEqual(
            req.move_ids.mapped('analytic_account_id'), self.analytic)
        self.assertEqual(order.analytic_count, 1)
        action = order.action_view_analytic()
        self.assertTrue(action['res_id'], self.analytic.id)

    def test_company(self):
        with self.assertRaises(ValidationError):
            vals = self.prepare_order_request_analytic(
                self.analytic2, self.main_company)
            self.env['stock.request.order'].create(vals)
