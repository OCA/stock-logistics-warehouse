# Copyright 2018 Camptocamp SA
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockWarehouseOrderpoint(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Get required Model
        cls.reordering_rule_model = cls.env['stock.warehouse.orderpoint']
        cls.stock_move_model = cls.env['stock.move']
        cls.product_model = cls.env['product.product']
        cls.product_ctg_model = cls.env['product.category']

        # Get required Model data
        cls.product_uom = cls.env.ref('uom.product_uom_unit')
        cls.location_stock = cls.env.ref('stock.stock_location_stock')
        cls.location_shelf1 = cls.env.ref('stock.stock_location_components')
        cls.location_customer = cls.env.ref('stock.stock_location_customers')
        cls.location_supplier = cls.env.ref('stock.stock_location_suppliers')

        # Create product category and product
        cls.product_ctg = cls._create_product_category()
        cls.product = cls._create_product()

        # Create Reordering Rule
        cls.reordering_record = cls.create_orderpoint()

    @classmethod
    def _create_product_category(cls):
        """Create a Product Category."""
        product_ctg = cls.product_ctg_model.create({
            'name': 'test_product_ctg',
        })
        return product_ctg

    @classmethod
    def _create_product(cls):
        """Create a Stockable Product."""
        product = cls.product_model.create({
            'name': 'Test Product',
            'categ_id': cls.product_ctg.id,
            'type': 'product',
            'uom_id': cls.product_uom.id,
        })
        return product

    @classmethod
    def create_orderpoint(cls):
        """Create a Reordering rule for the product."""
        record = cls.reordering_rule_model.create({
            'name': 'Reordering Rule',
            'product_id': cls.product.id,
            'product_min_qty': '1',
            'product_max_qty': '5',
            'qty_multiple': '1',
            'location_id': cls.location_stock.id,
        })
        return record

    def create_move(self, source_location, destination_location):
        move = self.env['stock.move'].create({
            'name': 'Test move',
            'product_id': self.product.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': 10,
            'quantity_done': 10,
            'location_id': source_location.id,
            'location_dest_id': destination_location.id
        })

        move._action_confirm()
        return move

    def test_product_qty(self):
        """Tests the product quantity in the Reordering rules"""
        # Create & process moves to test the product quantity
        move_in = self.create_move(
            self.location_supplier,
            self.location_stock,
        )
        move_out = self.create_move(
            self.location_stock,
            self.location_customer,
        )
        self.reordering_record.refresh()
        self.assertEqual(
            self.reordering_record.product_location_qty_available_not_res,
            0.0,
            'Quantity On Hand (Unreserved) does not match',
        )
        self.assertEqual(
            self.reordering_record.product_location_qty_available_not_res,
            self.product.qty_available_not_res,
            'Quantity On Hand (Unreserved) in the orderpoint '
            'does not match with the product.'
        )
        move_in._action_done()
        self.reordering_record.refresh()
        self.assertEqual(
            self.reordering_record.product_location_qty_available_not_res,
            10.0,
            'Quantity On Hand (Unreserved) does not match',
        )
        self.assertEqual(
            self.reordering_record.product_location_qty_available_not_res,
            self.product.qty_available_not_res,
            'Quantity On Hand (Unreserved) in the orderpoint '
            'does not match with the product.',
        )
        move_out._action_done()
        self.reordering_record.refresh()
        self.assertEqual(
            self.reordering_record.product_location_qty_available_not_res,
            0.0,
            'Quantity On Hand (Unreserved) does not match',
        )
        self.assertEqual(
            self.reordering_record.product_location_qty_available_not_res,
            self.product.qty_available_not_res,
            'Quantity On Hand (Unreserved) in the orderpoint '
            'does not match with the product.',
        )
