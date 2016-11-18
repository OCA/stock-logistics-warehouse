# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestProductStockLocation(common.TransactionCase):

    def setUp(self):
        super(TestProductStockLocation, self).setUp()
        # Get required Model
        self.product_stock_location_model = self.env['product.stock.location']
        self.stock_picking_model = self.env['stock.picking']
        self.product_model = self.env['product.product']
        self.product_ctg_model = self.env['product.category']

        # Get required Model data
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.location_stock = self.env.ref('stock.stock_location_stock')
        self.location_shelf1 = self.env.ref('stock.stock_location_components')
        self.location_customer = self.env.ref('stock.stock_location_customers')
        self.location_supplier = self.env.ref('stock.stock_location_customers')

        self.picking_in = self.env.ref('stock.picking_type_in')
        self.picking_out = self.env.ref('stock.picking_type_out')

        # Create product category and product
        self.product_ctg = self._create_product_category()
        self.product = self._create_product()

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

    def create_picking(self, picking_type, source_location,
                       destination_location):
        picking = self.stock_picking_model.create({
            'picking_type_id': picking_type.id,
            'location_id': source_location.id,
            'location_dest_id': destination_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': self.product.id,
                    'product_uom': self.product_uom.id,
                    'product_uom_qty': 10,
                    'location_id': source_location.id,
                    'location_dest_id': destination_location.id,
                })]
        })
        picking.action_confirm()
        return picking

    def test_product_qty(self):
        """Tests the product quantity in the locations"""
        # Create & process moves to test the product quantity
        picking_in_1 = self.create_picking(self.picking_in,
                                           self.location_supplier,
                                           self.location_shelf1)
        picking_in_2 = self.create_picking(self.picking_in,
                                           self.location_supplier,
                                           self.location_stock)
        picking_out_1 = self.create_picking(self.picking_out,
                                            self.location_shelf1,
                                            self.location_customer)

        psl_shelf1 = self.product_stock_location_model.search(
            [('product_id', '=', self.product.id),
             ('location_id', '=', self.location_shelf1.id)])
        psl_stock = self.product_stock_location_model.search(
            [('product_id', '=', self.product.id),
             ('location_id', '=', self.location_stock.id)])

        # Check Shelf 1
        self.assertEqual(psl_shelf1.product_location_qty,
                         0, 'On Hand Qty does not match')
        self.assertEqual(psl_shelf1.incoming_location_qty,
                         10, 'Incoming Qty does not match')
        self.assertEqual(psl_shelf1.outgoing_location_qty,
                         10, 'Outgoing Qty does not match')
        self.assertEqual(psl_shelf1.virtual_location_qty,
                         0, 'Forecasted Qty does not match')

        # Check Stock
        self.assertEqual(psl_stock.product_location_qty,
                         0, 'On Hand Qty does not match')
        self.assertEqual(psl_stock.incoming_location_qty,
                         20, 'Incoming Qty does not match')
        self.assertEqual(psl_stock.outgoing_location_qty,
                         10, 'Outgoing Qty does not match')
        self.assertEqual(psl_stock.virtual_location_qty,
                         10, 'Forecasted Qty does not match')

        # Check product
        self.assertEqual(self.product.qty_available, 0)
        self.assertEqual(self.product.incoming_qty, 20)
        self.assertEqual(self.product.outgoing_qty, 10)
        self.assertEqual(self.product.virtual_available, 10)

        # Move in 1
        picking_in_1.action_done()

        # Check Shelf 1
        self.assertEqual(psl_shelf1.product_location_qty,
                         10, 'On Hand Qty does not match')
        self.assertEqual(psl_shelf1.incoming_location_qty,
                         0, 'Incoming Qty does not match')
        self.assertEqual(psl_shelf1.outgoing_location_qty,
                         10, 'Outgoing Qty does not match')
        self.assertEqual(psl_shelf1.virtual_location_qty,
                         0, 'Forecasted Qty does not match')

        # Check Stock
        self.assertEqual(psl_stock.product_location_qty,
                         10, 'On Hand Qty does not match')
        self.assertEqual(psl_stock.incoming_location_qty,
                         10, 'Incoming Qty does not match')
        self.assertEqual(psl_stock.outgoing_location_qty,
                         10, 'Outgoing Qty does not match')
        self.assertEqual(psl_stock.virtual_location_qty,
                         10, 'Forecasted Qty does not match')

        # Check product
        self.assertEqual(self.product.qty_available, 10)
        self.assertEqual(self.product.incoming_qty, 10)
        self.assertEqual(self.product.outgoing_qty, 10)
        self.assertEqual(self.product.virtual_available, 10)

        # Move in 2
        picking_in_2.action_done()

        # Check Shelf 1
        self.assertEqual(psl_shelf1.product_location_qty,
                         10, 'On Hand Qty does not match')
        self.assertEqual(psl_shelf1.incoming_location_qty,
                         0, 'Incoming Qty does not match')
        self.assertEqual(psl_shelf1.outgoing_location_qty,
                         10, 'Outgoing Qty does not match')
        self.assertEqual(psl_shelf1.virtual_location_qty,
                         0, 'Forecasted Qty does not match')

        # Check Stock
        self.assertEqual(psl_stock.product_location_qty,
                         20, 'On Hand Qty does not match')
        self.assertEqual(psl_stock.incoming_location_qty,
                         0, 'Incoming Qty does not match')
        self.assertEqual(psl_stock.outgoing_location_qty,
                         10, 'Outgoing Qty does not match')
        self.assertEqual(psl_stock.virtual_location_qty,
                         10, 'Forecasted Qty does not match')

        # Check product
        self.assertEqual(self.product.qty_available, 20)
        self.assertEqual(self.product.incoming_qty, 0)
        self.assertEqual(self.product.outgoing_qty, 10)
        self.assertEqual(self.product.virtual_available, 10)

        # Move out 1
        picking_out_1.action_done()

        # Check Shelf 1
        self.assertEqual(psl_shelf1.product_location_qty,
                         0, 'On Hand Qty does not match')
        self.assertEqual(psl_shelf1.incoming_location_qty,
                         0, 'Incoming Qty does not match')
        self.assertEqual(psl_shelf1.outgoing_location_qty,
                         0, 'Outgoing Qty does not match')
        self.assertEqual(psl_shelf1.virtual_location_qty,
                         0, 'Forecasted Qty does not match')

        # Check Stock
        self.assertEqual(psl_stock.product_location_qty,
                         10, 'On Hand Qty does not match')
        self.assertEqual(psl_stock.incoming_location_qty,
                         0, 'Incoming Qty does not match')
        self.assertEqual(psl_stock.outgoing_location_qty,
                         0, 'Outgoing Qty does not match')
        self.assertEqual(psl_stock.virtual_location_qty,
                         10, 'Forecasted Qty does not match')

        # Check product
        self.assertEqual(self.product.qty_available, 10)
        self.assertEqual(self.product.incoming_qty, 0)
        self.assertEqual(self.product.outgoing_qty, 0)
        self.assertEqual(self.product.virtual_available, 10)
