# -*- coding: utf-8 -*-
# Copyright 2018 Akretion France
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockLocationLockdown(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestStockLocationLockdown, self).setUp(*args, **kwargs)
        self.main_stock_location = self.env.ref('stock.stock_location_stock')
        self.main_stock_location.block_stock_entrance = True
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.product = self.env.ref('product.product_product_27')

    def test_transfer_stock_in_locked_location(self):
        """
            Test to move stock within a location that should not accept
            Stock entrance.
        """
        move_vals = {
            'location_id': self.supplier_location.id,
            'location_dest_id': self.main_stock_location.id,
            'product_id': self.product.id,
            'product_uom_qty': self.product.qty_available + 1,
            'product_uom': 1,
            'name': 'test',
        }
        stock_move = self.env['stock.move'].create(move_vals)
        with self.assertRaises(ValidationError):
            stock_move.action_done()

    def test_transfer_stock_out_locked_location(self):
        """
            Test to move stock within a location that should not accept
            Stock entrance.
        """
        move_vals = {
            'location_id': self.main_stock_location.id,
            'location_dest_id': self.customer_location.id,
            'product_id': self.product.id,
            'product_uom_qty': self.product.qty_available + 1,
            'product_uom': 1,
            'name': 'test',
        }
        stock_move = self.env['stock.move'].create(move_vals)
        with self.assertRaises(ValidationError):
            stock_move.action_done()
