# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from dateutil.rrule import MONTHLY
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestStockDemandEstimate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.res_users_model = cls.env['res.users']
        cls.product_model = cls.env['product.product']
        cls.stock_location_model = cls.env['stock.location']

        cls.g_stock_manager = cls.env.ref('stock.group_stock_manager')
        cls.g_stock_user = cls.env.ref('stock.group_stock_user')
        cls.company = cls.env.ref('base.main_company')

        # Create users:
        cls.manager = cls._create_user(
            'user_1',
            [cls.g_stock_manager],
            cls.company,
        ).id
        cls.user = cls._create_user(
            'user_2',
            [cls.g_stock_user],
            cls.company,
        ).id
        cls.drt_monthly = cls.env['date.range.type'].create({
            'name': 'Month',
            'allow_overlap': False,
        })

        generator = cls.env['date.range.generator']
        generator = generator.create({
            'date_start': '1943-01-01',
            'name_prefix': '1943-',
            'type_id': cls.drt_monthly.id,
            'duration_count': 1,
            'unit_of_time': MONTHLY,
            'count': 12,
        })
        generator.action_apply()

        # Create a product:
        cls.product1 = cls.product_model.create({
            'name': 'Test Product 1',
            'type': 'product',
            'default_code': 'PROD1',
        })
        # Create a location:
        cls.location = cls.stock_location_model.create({
            'name': 'Place',
            'usage': 'production',
        })

    @classmethod
    def _create_user(cls, login, groups, company):
        group_ids = [group.id for group in groups]
        user = cls.res_users_model.create({
            'name': login,
            'login': login,
            'password': 'demo',
            'email': 'example@yourcompany.com',
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'groups_id': [(6, 0, group_ids)],
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
            'product_ids': [(6, 0, [self.product1.id])],
        })
        wiz.create_sheet()
        sheets = self.env['stock.demand.estimate.sheet'].search([])
        for sheet in sheets:
            self.assertEqual(
                len(sheet.line_ids),
                12,
                'There should be 12 lines.',
            )
            self.assertEqual(
                fields.Date.to_string(sheet.date_start),
                '1943-01-01',
                'The date start should be 1943-01-01',
            )
            self.assertEqual(
                fields.Date.to_string(sheet.date_end),
                '1943-12-31',
                'The date end should be 1943-12-31',
            )
            self.assertEqual(
                sheet.location_id.id,
                self.location.id,
                'Wrong location',
            )
            for line in sheet.line_ids:
                line.product_uom_qty = 1
                self.assertEqual(
                    line.product_id.id,
                    self.product1.id,
                    'The product does not match in the line',
                )
                self.assertEqual(
                    line.location_id.id,
                    self.location.id,
                    'The product does not match in the line',
                )
            sheet.button_validate()
            ranges = self.env['date.range'].search(
                [('type_id', '=', self.drt_monthly.id)],
            )
            estimates = self.env['stock.demand.estimate'].search(
                [('date_range_id', 'in', ranges.ids)]
            )
            self.assertEqual(
                len(estimates),
                12,
                'There should be 12 estimate records.',
            )
            for estimate in estimates:
                self.assertEqual(
                    estimate.product_id.id,
                    self.product1.id,
                    'The product does not match in the estimate',
                )
                self.assertEqual(
                    estimate.location_id.id,
                    self.location.id,
                    'The product does not match in the estimate',
                )

        sheets = self.env['stock.demand.estimate.sheet'].search([])
        for sheet in sheets:
            sheet.unlink()
        wiz = self.env['stock.demand.estimate.wizard']
        wiz = wiz.create({
            'date_start': '1943-01-01',
            'date_end': '1943-12-31',
            'location_id': self.location.id,
            'date_range_type_id': self.drt_monthly.id,
            'product_ids': [(6, 0, [self.product1.id])],
        })
        wiz.create_sheet()
        sheets = self.env['stock.demand.estimate.sheet'].search([])
        for sheet in sheets:
            for line in sheet.line_ids:
                self.assertEqual(
                    line.product_uom_qty,
                    1,
                    'The quantity should be 1',
                )

    def test_invalid_dates(self):

        wiz = self.env['stock.demand.estimate.wizard']
        with self.assertRaises(ValidationError):
            wiz.create({
                'date_start': '1943-12-31',
                'date_end': '1943-01-01',
                'location_id': self.location.id,
                'date_range_type_id': self.drt_monthly.id,
                'product_ids': [(6, 0, [self.product1.id])],
            })
