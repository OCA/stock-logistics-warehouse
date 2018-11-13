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
        self.warehouse_1 = self.env.ref('stock.warehouse0')

    def test_00_lot_product_available_today(self):
        lot_obj = self.env['stock.production.lot']
        removal_date = fields.Datetime.from_string(
            fields.Datetime.now()) + timedelta(days=5)
        # First create lot
        vals = {'removal_date': removal_date,
                'product_id': self.product_1.id
                }
        self.lot_1 = lot_obj.create(vals)
        # Create Inventory for product
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
        self.assertEqual(self.product_1.qty_available, 10)
        self.assertEqual(self.product_1.qty_expired, 0)
        self.assertEqual(self.product_1.outgoing_expired_qty, 0)

        removal_date = fields.Datetime.from_string(
            fields.Datetime.now()) + timedelta(days=-5)
        vals = {'removal_date': removal_date,
                'product_id': self.product_1.id
                }
        self.lot_2 = lot_obj.create(vals)
        # Create Inventory for product
        inventory = self.env['stock.inventory'].create({
            'name': 'Initial inventory',
            'filter': 'partial',
            'line_ids': [(0, 0, {
                'product_id': self.product_1.id,
                'prod_lot_id': self.lot_2.id,
                'product_uom_id': self.product_1.uom_id.id,
                'product_qty': 20,
                'location_id': self.warehouse_1.lot_stock_id.id
            })]
        })
        inventory.action_done()
        self.product_1.refresh()
        self.assertEqual(self.product_1.qty_available, 10)
        self.assertEqual(self.product_1.qty_expired, 20)
        self.assertEqual(self.product_1.outgoing_expired_qty, 0)

    def test_outgoing_expired_lot(self):
        lot_obj = self.env['stock.production.lot']
        removal_date = fields.Datetime.from_string(
            fields.Datetime.now()) + timedelta(days=-5)
        stock_location = self.warehouse_1.lot_stock_id
        # First create lot
        vals = {'removal_date': removal_date,
                'product_id': self.product_1.id
                }
        self.lot_1 = lot_obj.create(vals)
        # Create Inventory for product
        inventory = self.env['stock.inventory'].create({
            'name': 'Initial inventory',
            'filter': 'partial',
            'line_ids': [(0, 0, {
                'product_id': self.product_1.id,
                'prod_lot_id': self.lot_1.id,
                'product_uom_id': self.product_1.uom_id.id,
                'product_qty': 10,
                'location_id': stock_location.id
            })]
        })
        inventory.action_done()
        self.assertEqual(self.product_1.qty_available, 0)
        self.assertEqual(self.product_1.qty_expired, 10)
        self.assertEqual(self.product_1.outgoing_expired_qty, 0)
        # if we create a picking out for the expired lot, as long as the
        # expired quant is not reserved for the picking, the qty_expired
        # remains the same and the outgoing_expired_qty is 0 since it's
        # impossible to predict which lot will be
        # reserved....
        customer_location = self.env.ref('stock.stock_location_suppliers')
        stock_picking_obj = self.env['stock.picking']
        picking_out = stock_picking_obj.create({
            'picking_type_id': self.env.ref(
                'stock.picking_type_out').id,
            'location_id': stock_location.id,
            'location_dest_id': customer_location.id
        })
        stock_move_obj = self.env['stock.move']
        stock_move_obj.create({
            'name': self.product_1.name,
            'product_id': self.product_1.id,
            'product_uom_qty': 10,
            'product_uom': self.product_1.uom_id.id,
            'picking_id': picking_out.id,
            'location_id': stock_location.id,
            'location_dest_id': customer_location.id})
        picking_out.action_confirm()
        self.assertEqual(self.product_1.qty_available, 0)
        self.assertEqual(self.product_1.outgoing_qty, 10)
        self.assertEqual(self.product_1.qty_expired, 10)
        self.assertEqual(self.product_1.outgoing_expired_qty, 0)

        for move in picking_out.move_lines:
            self.assertEqual(move.state, 'confirmed',
                             'Wrong state of move line.')
        # Product assign to outgoing shipments...
        picking_out.action_assign()

        # once the expired lot is reserved for the outgoing picking it
        # appears into the outgoing_expired_qty
        self.assertEqual(self.product_1.qty_available, 0)
        self.assertEqual(self.product_1.qty_expired, 0)
        self.assertEqual(self.product_1.outgoing_qty, 0)
        self.assertEqual(self.product_1.outgoing_expired_qty, 10)

    def test_01_lot_product_available_tomorrow(self):
        lot_obj = self.env['stock.production.lot']
        removal_date = fields.Datetime.from_string(fields.Datetime.now())
        # First create lot
        vals = {'removal_date': removal_date,
                'product_id': self.product_1.id
                }
        self.lot_1 = lot_obj.create(vals)
        # Create Inventory for product
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
        # Unfortunately the lot expired today
        self.assertEqual(self.product_1.qty_available, 0)
        self.assertEqual(self.product_1.qty_expired, 10)

    def test_02_lot_product_available_from_to(self):
        lot_obj = self.env['stock.production.lot']
        removal_date = fields.Datetime.from_string(fields.Datetime.now())
        # First create lot
        vals = {'removal_date': removal_date,
                'product_id': self.product_1.id
                }
        self.lot_1 = lot_obj.create(vals)
        # Create Inventory for product
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
        # Get pivot date on yesterday
        from_date = fields.Datetime.to_string(
            fields.Datetime.from_string(
                fields.Datetime.now()) + timedelta(days=-1))
        self.assertEqual(
            self.product_1.with_context(from_date=from_date).qty_available,
            10)
        # Get pivot date from  yesterday to today
        from_date = fields.Datetime.to_string(
            fields.Datetime.from_string(
                fields.Datetime.now()) + timedelta(days=-1))
        to_date = fields.Datetime.now()
        self.assertEqual(
            self.product_1.with_context(
                from_date=from_date, to_date=to_date).qty_available,
            0)

    def test_03_configuration(self):
        wizard = self.env['stock.config.settings'].create({})

        self.assertEquals(
            wizard.stock_qty_available_lot_expired,
            True,
            'The default stock_qty_available_lot_expired should be True')

        wizard.stock_qty_available_lot_expired = False
        wizard.execute()

        param_obj = self.env['ir.config_parameter']
        value = param_obj.get_param('stock_qty_available_lot_expired')
        self.assertEquals(
            value,
            False,
            'The set value of stock_qty_available_lot_expired should be False')

    def test_action_open_expired_quants(self):
        with mock.patch.object(fields.Datetime, 'now') as patch_now:
            patch_now.return_value = 'dt_now'
            res = self.product_1.action_open_expired_quants()
        expected_domain = [
            '&',
            '&',
            ('product_id', 'in', [self.product_1.id]),
            ('lot_id', '!=', False),
            '|',
            ('lot_id.removal_date', '=', False),
            ('lot_id.removal_date', '<=', 'dt_now')]
        self.assertListEqual(res.get('domain'), expected_domain)

    def test_get_original_domain_locations(self):
        domain = self.product_1._get_original_domain_locations()
        self.assertNotIn(
            'lot_id',
            domain,
        )

    def test_03_lot_product_outgoing_disable(self):
        from dateutil.relativedelta import relativedelta
        lot_obj = self.env['stock.production.lot']
        removal_date = fields.Datetime.from_string(
            fields.Datetime.now()) + relativedelta(days=-1)
        # First create lot
        vals = {'removal_date': removal_date,
                'product_id': self.product_1.id
                }
        self.lot_1 = lot_obj.create(vals)
        # Create Inventory for product
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
        vals = {
            'name': 'Move OUT',
            'date': fields.Datetime.now(),
            'location_id': self.ref('stock.stock_location_stock'),
            'location_dest_id': self.ref('stock.stock_location_customers'),
            'product_id': self.product_1.id,
            'product_uom_qty': 10.0,
            'product_uom': self.product_1.uom_id.id
        }
        move = self.env['stock.move'].create(vals)
        move.action_confirm()
        move.action_assign()
        out_qty = self.product_1.with_context(
            disable_check_expired_lots=True).outgoing_qty
        self.assertEquals(
            10.0,
            out_qty
        )
