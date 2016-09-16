# -*- coding: utf-8 -*-
# © 2016 Esther Martín - AvanzOSC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.tests.common as common


class TestStockInventoryLinePrice(common.TransactionCase):

    def setUp(self):
        super(TestStockInventoryLinePrice, self).setUp()
        self.product = self.env.ref('product.product_product_6')
        self.stock_move_obj = self.env['stock.move']
        self.inventory = self.env['stock.inventory'].create({
            'name': 'Test Inventory',
            'filter': 'product',
            'product_id': self.product.id
            })

    def test_change_price(self):
        self.inventory.prepare_inventory()
        self.assertEqual(len(self.inventory.line_ids), 1)
        self.assertEqual(
            self.inventory.line_ids[0].theoretical_std_price,
            self.inventory.line_ids[0].standard_price)
        self.assertEqual(self.product.standard_price,
                         self.inventory.line_ids[0].standard_price)
        self.inventory.line_ids[0].standard_price += 10
        self.assertNotEqual(
            self.inventory.line_ids[0].theoretical_std_price,
            self.inventory.line_ids[0].standard_price)
        self.inventory.action_done()
        self.assertEqual(self.product.standard_price,
                         self.inventory.line_ids[0].standard_price)

    def test_change_price_move(self):
        self.inventory.prepare_inventory()
        self.assertEqual(len(self.inventory.line_ids), 1)
        self.inventory.line_ids[0].standard_price += 10
        self.inventory.line_ids[0].product_qty += 10
        self.inventory.action_done()
        move = self.stock_move_obj.search([
            ('product_id', '=', self.product.id),
            ('inventory_id', '=', self.inventory.id)])
        self.assertEqual(
            self.inventory.line_ids[0].standard_price, move.price_unit)
        self.assertEqual(self.product.standard_price, move.price_unit)
