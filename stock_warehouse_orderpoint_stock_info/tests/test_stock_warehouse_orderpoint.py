# -*- coding: utf-8 -*-
# Copyright 2016 OdooMRP Team
# Copyright 2016 AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2016-17 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


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
        self.dest_location = self.env.ref('stock.stock_location_stock')
        self.location = self.env.ref('stock.stock_location_locations_partner')
        self.picking = self.env.ref('stock.picking_type_in')

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
            'location_id': self.dest_location.id,
        })
        return record

    def create_stock_move(self):
        """Create a Stock Move."""
        move = self.stock_move_model.create({
            'name': 'Reordering Product',
            'product_id': self.product.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': '10.0',
            'picking_type_id': self.picking.id,
            'location_id': self.location.id,
            'location_dest_id': self.dest_location.id
        })
        move.action_confirm()
        return move

    def test_product_qty(self):
        """Tests the product quantity in the Reordering rules"""
        # Create & process moves to test the product quantity
        move = self.create_stock_move()
        self.reordering_record.refresh()
        self.assertEqual(self.reordering_record.incoming_location_qty,
                         self.product.incoming_qty,
                         'Incoming Qty does not match')
        self.assertEqual(self.reordering_record.virtual_location_qty,
                         self.product.virtual_available,
                         'Virtual Qty does not match')
        move.action_done()
        self.reordering_record.refresh()
        self.assertEqual(self.reordering_record.product_location_qty,
                         self.product.qty_available,
                         'Available Qty does not match')
        self.assertEqual(self.reordering_record.virtual_location_qty,
                         self.product.virtual_available,
                         'Virtual Qty does not match')
