# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import mock
from odoo import fields
from odoo.tests import common
from datetime import timedelta


class TestProductProduct(common.TransactionCase):

    def setUp(self):
        super(TestProductProduct, self).setUp()
        param_obj = self.env['ir.config_parameter']
        param_obj.set_param('stock_qty_available_lot_expired', True)

        vals = {'name': 'Product with lot',
                'type': 'product'
                }
        self.product_1 = self.env['product.product'].create(vals)
        self.product_1.tracking = 'lot'
        self.product_template = self.product_1.product_tmpl_id
        vals = {'name': 'Product variant with lot',
                'type': 'product',
                'product_tmpl_id': self.product_template.id,
                }
        self.product_2 = self.env['product.product'].create(vals)
        self.product_2.tracking = 'lot'
        self.warehouse_1 = self.env.ref('stock.warehouse0')

        # on product 1 add a quantity of 10 with a removal time set to now +
        #  5 days
        removal_date = fields.Datetime.from_string(
            fields.Datetime.now()) + timedelta(days=5)
        # First create lot
        vals = {'removal_date': removal_date,
                'product_id': self.product_1.id
                }
        lot_obj = self.env['stock.production.lot']
        self.lot_1 = lot_obj.create(vals)
        inventory = self.env['stock.inventory'].create({
            'name': 'Initial inventory',
            'filter': 'partial',
            'line_ids': [(0, 0, {
                'product_id': self.product_1.id,
                'prod_lot_id': self.lot_1.id,
                'product_uom_id': self.product_1.uom_id.id,
                'product_qty': 10,
                'location_id': self.warehouse_1.lot_stock_id.id
            })]
        })
        inventory.action_done()
        # on product 2 add a quantity of 20 with a removal time set to 5
        # days ago
        removal_date = fields.Datetime.from_string(
            fields.Datetime.now()) + timedelta(days=-5)
        vals = {'removal_date': removal_date,
                'product_id': self.product_2.id
                }
        self.lot_2 = lot_obj.create(vals)
        inventory = self.env['stock.inventory'].create({
            'name': 'Initial inventory',
            'filter': 'partial',
            'line_ids': [(0, 0, {
                'product_id': self.product_2.id,
                'prod_lot_id': self.lot_2.id,
                'product_uom_id': self.product_2.uom_id.id,
                'product_qty': 20,
                'location_id': self.warehouse_1.lot_stock_id.id
            })]
        })
        inventory.action_done()

    def test_product_template_expiry(self):
        # Check check expired
        self.assertTrue(self.product_template.check_expired_lots)

        # check quantity  on template
        # today
        self.assertEqual(self.product_template.qty_available, 10.0)
        self.assertEqual(self.product_template.qty_expired, 20.0)

        # 5 days ago
        removal_date = fields.Datetime.to_string(
            fields.Datetime.from_string(
                fields.Datetime.now()) + timedelta(days=-6)
        )
        self.product_template = self.product_template.with_context(
            from_date=removal_date)
        self.assertEqual(self.product_template.qty_available, 30.0)
        self.assertEqual(self.product_template.qty_expired, 0.0)

        # 5 days later
        removal_date = fields.Datetime.to_string(
            fields.Datetime.from_string(
                fields.Datetime.now()) + timedelta(days=5)
        )
        self.product_template = self.product_template.with_context(
            to_date=removal_date)
        self.assertEqual(self.product_template.qty_available, 0.0)
        self.assertEqual(self.product_template.qty_expired, 30.0)

    def test_action_open_expired_quants(self):
        with mock.patch.object(fields.Datetime, 'now') as patch_now:
            patch_now.return_value = 'dt_now'
            res = self.product_template.action_open_expired_quants()
        expected_domain = [
            '&',
            ('product_id', 'in', [self.product_1.id, self.product_2.id]),
            '&',
            ('lot_id', '!=', False),
            '&',
            ('lot_id.removal_date', '!=', False),
            ('lot_id.removal_date', '<=', 'dt_now')]
        self.assertListEqual(res.get('domain'), expected_domain)

    def test_action_open_quants(self):
        with mock.patch.object(fields.Datetime, 'now') as patch_now:
            patch_now.return_value = 'dt_now'
            res = self.product_template.action_open_quants()
        expected_domain = [
            '&',
            ('product_id', 'in', [self.product_1.id, self.product_2.id]),
            '|',
            ('lot_id', '=', False),
            '&',
            ('lot_id', '!=', False),
            '|',
            ('lot_id.removal_date', '=', False),
            ('lot_id.removal_date', '>', 'dt_now')]
        self.assertListEqual(res.get('domain'), expected_domain)
