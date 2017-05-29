# -*- coding: utf-8 -*-
# © 2015 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMerge(TransactionCase):
    """Test the potential quantity on a product with a multi-line BoM"""

    def setUp(self):
        super(TestMerge, self).setUp()

        # Get the warehouses
        self.wh_main = self.browse_ref('stock.warehouse0')
        self.wh_ch = self.browse_ref('stock.stock_warehouse_shop0')

        # Get a product
        self.product = self.browse_ref('product.product_product_4')

        # Zero out the inventory of the product
        inventory = self.env['stock.inventory'].create(
            {'name': 'Remove product for test',
             'location_id': self.ref('stock.stock_location_locations'),
             'filter': 'product',
             'product_id': self.product.id})
        inventory.prepare_inventory()
        inventory.reset_real_qty()
        inventory.action_done()

        # Make sure we have some products in Chicago
        inventory = self.env['stock.inventory'].create(
            {'name': 'Test stock available for reservation',
             'location_id': self.wh_ch.lot_stock_id.id,
             'filter': 'none'})
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': self.product.id,
            'location_id': self.wh_ch.lot_stock_id.id,
            'product_qty': 10.0})
        inventory.action_done()

    def test_merge(self):
        quant_obj = self.env['stock.quant']
        domain = [('location_id', '=', self.wh_ch.lot_stock_id.id),
                  ('product_id', '=', self.product.id)]

        quants = quant_obj.search(domain)
        self.assertEqual(len(quants), 1, "There should be 1 quant")

        # Make a reservation to split the quant
        move = self.env['stock.move'].create(
            {'name': 'Test move',
             'product_id': self.product.id,
             'location_id': self.wh_ch.lot_stock_id.id,
             'location_dest_id': self.wh_main.lot_stock_id.id,
             'product_uom_qty': 5.0,
             'product_uom': self.product.uom_id.id})
        move.action_confirm()
        move.action_assign()

        quants = quant_obj.search(domain)
        self.assertEqual(len(quants), 2, "There should be 2 quants")

        # Cancel the move : the quants should be merged back together
        move.action_cancel()

        quants = quant_obj.search(domain)
        self.assertEqual(len(quants), 1, "There should be 1 quant")
