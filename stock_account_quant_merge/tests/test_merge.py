# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.stock.tests.common import TestStockCommon


class TestMerge(TestStockCommon):
    """Test the potential quantity on a product with a multi-line BoM"""

    def setUp(self):
        super(TestMerge, self).setUp()
        loc_supplier_id = self.env.ref('stock.stock_location_suppliers')
        self.loc_stock = self.env.ref('stock.stock_location_stock')
        self.loc_scrap = self.env.ref('stock.stock_location_scrapped')
        self.product = self.env.ref('product.product_product_36')

        # Zero out the inventory of the product
        inventory = self.env['stock.inventory'].create(
            {'name': 'Remove product for test',
             'location_id': self.loc_stock.id,
             'filter': 'product',
             'product_id': self.product.id})
        inventory.prepare_inventory()
        inventory.reset_real_qty()
        inventory.action_done()

        self.picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']

        self.picking_type = self.env.ref('stock.picking_type_in')

        # Change the cost method to 'Real Price'
        self.product.cost_method = 'real'

        self.picking_1 = self.picking_obj.create(
            {'picking_type_id': self.picking_type.id,
             'location_id': loc_supplier_id.id,
             'location_dest_id': self.loc_stock.id
             })
        move_obj.create({'name': '/',
                         'picking_id': self.picking_1.id,
                         'product_uom': self.product.uom_id.id,
                         'location_id': loc_supplier_id.id,
                         'location_dest_id': self.loc_stock.id,
                         'product_id': self.product.id,
                         'price_unit': 10,
                         'product_uom_qty': 10})
        self.picking_1.action_confirm()
        self.picking_1.action_assign()
        self.picking_1.action_done()

        self.picking_2 = self.picking_obj.create(
            {'picking_type_id': self.picking_type.id,
             'location_id': loc_supplier_id.id,
             'location_dest_id': self.loc_stock.id
             })
        move_obj.create({'name': '/',
                         'picking_id': self.picking_2.id,
                         'product_uom': self.product.uom_id.id,
                         'location_id': loc_supplier_id.id,
                         'location_dest_id': self.loc_stock.id,
                         'product_id': self.product.id,
                         'price_unit': 20,
                         'product_uom_qty': 10})
        self.picking_2.action_confirm()
        self.picking_2.action_assign()
        self.picking_2.action_done()

    def test_merge(self):
        quant_obj = self.env['stock.quant']
        domain = [('location_id', '=', self.loc_stock.id),
                  ('product_id', '=', self.product.id)]

        quants = quant_obj.search(domain)
        self.assertEqual(len(quants), 2, "There should be 2 quants")

        # Make a reservation to split the quants
        move_1 = self.env['stock.move'].create(
            {'name': 'Test move',
             'product_id': self.product.id,
             'location_id': self.loc_stock.id,
             'location_dest_id': self.loc_scrap.id,
             'product_uom_qty': 15.0,
             'product_uom': self.product.uom_id.id})
        move_1.action_confirm()
        move_1.action_assign()

        # Make a reservation to split the quants
        move_2 = self.env['stock.move'].create(
            {'name': 'Test move',
             'product_id': self.product.id,
             'location_id': self.loc_stock.id,
             'location_dest_id': self.loc_scrap.id,
             'product_uom_qty': 3.0,
             'product_uom': self.product.uom_id.id})
        move_2.action_confirm()
        move_2.action_assign()

        quants = quant_obj.search(domain)
        self.assertEqual(len(quants), 4, "There should be 4 quants")

        # Cancel the second move : the quants with unit cost 20 should be
        # merged back together
        move_2.action_cancel()
        quants = quant_obj.search(domain)
        self.assertEqual(len(quants), 3, "There should be 3 quants")

        # Cancel the first move : the quants with unit cost 20 should be
        # merged back together
        move_1.action_cancel()
        quants = quant_obj.search(domain)
        self.assertEqual(len(quants), 2, "There should be 2 quants")
