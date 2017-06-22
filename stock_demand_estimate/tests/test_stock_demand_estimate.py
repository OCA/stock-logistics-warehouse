# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import common
from dateutil.rrule import MONTHLY
from odoo.exceptions import ValidationError


class TestStockDemandEstimate(common.TransactionCase):

    def setUp(self):
        super(TestStockDemandEstimate, self).setUp()
        self.res_users_model = self.env['res.users']
        self.product_model = self.env['product.product']
        self.stock_location_model = self.env['stock.location']

        self.g_stock_manager = self.env.ref('stock.group_stock_manager')
        self.g_stock_user = self.env.ref('stock.group_stock_user')
        self.company = self.env.ref('base.main_company')

        # Create users:
        self.manager = self._create_user(
            'user_1', [self.g_stock_manager], self.company).id
        self.user = self._create_user(
            'user_2', [self.g_stock_user], self.company).id
        self.drt_monthly = self.env['date.range.type'].create(
            {'name': 'Month',
             'allow_overlap': False})

        generator = self.env['date.range.generator']
        generator = generator.create({
            'date_start': '1943-01-01',
            'name_prefix': '1943-',
            'type_id': self.drt_monthly.id,
            'duration_count': 1,
            'unit_of_time': MONTHLY,
            'count': 12})
        generator.action_apply()

        # Create a product:
        self.product1 = self.product_model.create({
            'name': 'Test Product 1',
            'type': 'product',
            'default_code': 'PROD1',
        })
        # Create a location:
        self.location = self.stock_location_model.create({
            'name': 'Place',
            'usage': 'production'
        })

    def _create_user(self, login, groups, company):
        group_ids = [group.id for group in groups]
        user = self.res_users_model.create({
            'name': login,
            'login': login,
            'password': 'demo',
            'email': 'example@yourcompany.com',
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'groups_id': [(6, 0, group_ids)]
        })
        return user

    def test_demand_estimate(self):
        """Tests creation of demand estimates."""
        sheets = self.env['stock.demand.estimate.sheet'].search([])
        for sheet in sheets:
            sheet.unlink()
        wiz = self.env['stock.demand.estimate.wizard']
        wiz = wiz.create({
            'date_start': '1943-01-01',
            'date_end': '1943-12-31',
            'location_id': self.location.id,
            'date_range_type_id': self.drt_monthly.id,
            'product_ids': [(6, 0, [self.product1.id])]})
        wiz.create_sheet()
        sheets = self.env['stock.demand.estimate.sheet'].search([])
        for sheet in sheets:

            self.assertEquals(len(sheet.line_ids), 12,
                              'There should be 12 lines.')
            self.assertEquals(sheet.date_start, '1943-01-01',
                              'The date start should be 1943-01-01')
            self.assertEquals(sheet.date_end, '1943-12-31',
                              'The date end should be 1943-12-31')
            self.assertEquals(sheet.location_id.id, self.location.id,
                              'Wrong location')
            self.assertEquals(sheet.product_ids.ids, [self.product1.id],
                              'Wrong products')
            for line in sheet.line_ids:
                line.product_uom_qty = 1
                self.assertEquals(line.product_id.id, self.product1.id,
                                  'The product does not match in the line')
                self.assertEquals(line.location_id.id, self.location.id,
                                  'The product does not match in the line')
            sheet.button_validate()
            estimates = self.env['stock.demand.estimate'].search([(
                'date_range_type_id', '=', self.drt_monthly)])
            self.assertEquals(len(estimates), 12, 'There should be 12 '
                                                  'estimate records.')
            for estimate in estimates:
                self.assertEquals(estimate.product_id.id, self.product1.id,
                                  'The product does not match in the estimate')
                self.assertEquals(estimate.location_id.id, self.location.id,
                                  'The product does not match in the estimate')

        sheets = self.env['stock.demand.estimate.sheet'].search([])
        for sheet in sheets:
            sheet.unlink()
        wiz = self.env['stock.demand.estimate.wizard']
        wiz = wiz.create({
            'date_start': '1943-01-01',
            'date_end': '1943-12-31',
            'location_id': self.location.id,
            'date_range_type_id': self.drt_monthly.id,
            'product_ids': [(6, 0, [self.product1.id])]})
        wiz.create_sheet()
        sheets = self.env['stock.demand.estimate.sheet'].search([])
        for sheet in sheets:
            for line in sheet.line_ids:
                self.assertEquals(line.product_uom_qty, 1,
                                  'The quantity should be 1')

    def test_invalid_dates(self):

        wiz = self.env['stock.demand.estimate.wizard']
        with self.assertRaises(ValidationError):
            wiz.create({
                'date_start': '1943-12-31',
                'date_end': '1943-01-01',
                'location_id': self.location.id,
                'date_range_type_id': self.drt_monthly.id,
                'product_ids': [(6, 0, [self.product1.id])]})
