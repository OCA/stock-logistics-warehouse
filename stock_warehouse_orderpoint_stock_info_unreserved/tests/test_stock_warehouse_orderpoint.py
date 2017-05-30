# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestStockWarehouseOrderpoint(common.TransactionCase):

    def setUp(self):
        super(TestStockWarehouseOrderpoint, self).setUp()
        # Get required Model
        self.reordering_rule_model = self.env['stock.warehouse.orderpoint']
        self.stock_move_model = self.env['stock.move']
        self.product_model = self.env['product.product']
        self.product_ctg_model = self.env['product.category']

        # Get required Model data
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.location_stock = self.env.ref('stock.stock_location_stock')
        self.location_shelf1 = self.env.ref('stock.stock_location_components')
        self.location_customer = self.env.ref('stock.stock_location_customers')
        self.location_supplier = self.env.ref('stock.stock_location_suppliers')

        # Create product category and product
        self.product_ctg = self._create_product_category()
        self.product = self._create_product()

        # Create Reordering Rule
        self.reordering_record = self.create_orderpoint()

    def _create_product_category(self):
        """Create a Product Category."""
        product_ctg = self.product_ctg_model.create({
            'name': 'test_product_ctg',
            'type': 'normal',
        })
        return product_ctg

    def _create_product(self):
        """Create a Stockable Product."""
        product = self.product_model.create({
            'name': 'Test Product',
            'categ_id': self.product_ctg.id,
            'type': 'product',
            'uom_id': self.product_uom.id,
        })
        return product

    def create_orderpoint(self):
        """Create a Reordering rule for the product."""
        record = self.reordering_rule_model.create({
            'name': 'Reordering Rule',
            'product_id': self.product.id,
            'product_min_qty': '1',
            'product_max_qty': '5',
            'qty_multiple': '1',
            'location_id': self.location_stock.id,
        })
        return record

    def create_move(self, source_location, destination_location):
        move = self.env['stock.move'].create({
            'name': 'Test move',
            'product_id': self.product.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': 10,
            'location_id': source_location.id,
            'location_dest_id': destination_location.id}
        )

        move.action_confirm()
        return move

    def test_product_qty(self):
        """Tests the product quantity in the Reordering rules"""
        # Create & process moves to test the product quantity
        move_in = self.create_move(self.location_supplier, self.location_stock)
        move_out = self.create_move(self.location_stock,
                                    self.location_customer)
        self.reordering_record.refresh()
        self.assertEqual(self.reordering_record.
                         product_location_qty_available_not_res,
                         0.0,
                         'Quantity On Hand (Unreserved) does not match')
        self.assertEqual(self.reordering_record.
                         product_location_qty_available_not_res,
                         self.product.qty_available_not_res,
                         'Quantity On Hand (Unreserved) in the orderpoint '
                         'does not match with the product.')
        move_in.action_done()
        self.reordering_record.refresh()
        self.assertEqual(self.reordering_record.
                         product_location_qty_available_not_res,
                         10.0,
                         'Quantity On Hand (Unreserved) does not match')
        self.assertEqual(self.reordering_record.
                         product_location_qty_available_not_res,
                         self.product.qty_available_not_res,
                         'Quantity On Hand (Unreserved) in the orderpoint '
                         'does not match with the product.')
        move_out.action_assign()
        self.reordering_record.refresh()
        self.assertEqual(self.reordering_record.
                         product_location_qty_available_not_res,
                         0.0,
                         'Quantity On Hand (Unreserved) does not match')
        self.assertEqual(self.reordering_record.
                         product_location_qty_available_not_res,
                         self.product.qty_available_not_res,
                         'Quantity On Hand (Unreserved) in the orderpoint '
                         'does not match with the product.')
