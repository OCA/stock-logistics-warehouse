# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import UserError


class TestOperationPackageMandatory(common.TransactionCase):

    def setUp(self):
        super(TestOperationPackageMandatory, self).setUp()
        move_obj = self.env['stock.move']
        self.picking_type_int = self.env.ref('stock.picking_type_internal')
        # Set Destination Package presence mandatory
        self.picking_type_int.destination_package_mandatory = True
        vals = {'name': 'PICKING 1',
                'location_id': self.ref('stock.stock_location_stock'),
                'location_dest_id': self.ref('stock.stock_location_output'),
                'picking_type_id': self.picking_type_int.id
                }
        self.picking_1 = self.env['stock.picking'].create(vals)
        vals = {'name': 'PRODUCT 24',
                'product_id': self.ref('product.product_product_24'),
                'product_uom_qty': 5.0,
                'product_uom':
                    self.env.ref('product.product_product_24').uom_id.id,
                'location_id': self.ref('stock.stock_location_stock'),
                'location_dest_id': self.ref('stock.stock_location_output'),
                'picking_id': self.picking_1.id
                }
        self.move_1 = move_obj.create(vals)
        vals = {'name': 'PRODUCT 25',
                'product_id': self.ref('product.product_product_25'),
                'product_uom_qty': 1.0,
                'product_uom':
                    self.env.ref('product.product_product_25').uom_id.id,
                'location_id': self.ref('stock.stock_location_stock'),
                'location_dest_id': self.ref('stock.stock_location_output'),
                'picking_id': self.picking_1.id
                }
        self.move_2 = move_obj.create(vals)

    def test_00_transfer(self):
        self.picking_1.action_confirm()
        self.picking_1.action_assign()
        self.assertEqual(2,
                         len(self.picking_1.pack_operation_ids),
                         'The amount of pack operations is incorrect')
        # Set package on the first pack operation
        package1 = self.env['stock.quant.package'].create({'name': 'PACK1'})
        operation_24 = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id ==
            self.env.ref('product.product_product_24'))
        operation_25 = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id ==
            self.env.ref('product.product_product_25'))
        # Set Qty Done
        operation_24.qty_done = 5.0
        operation_25.qty_done = 1.0
        # Set Package on first operation
        operation_24.write(
            {'result_package_id': package1.id, 'product_qty': 5.0})
        with self.assertRaises(UserError):
            self.picking_1.do_new_transfer()
        operation_25.write(
            {'result_package_id': package1.id, 'product_qty': 1.0})
        self.picking_1.do_new_transfer()

    def test_01_transfer_not_mandatory(self):
        self.picking_type_int.destination_package_mandatory = False
        self.picking_1.action_confirm()
        self.picking_1.action_assign()
        operation_24 = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id ==
            self.env.ref('product.product_product_24'))
        operation_25 = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id ==
            self.env.ref('product.product_product_25'))
        # Set Qty Done
        operation_24.qty_done = 5.0
        operation_25.qty_done = 1.0
        self.picking_1.do_new_transfer()
