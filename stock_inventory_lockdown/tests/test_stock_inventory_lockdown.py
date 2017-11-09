# -*- coding: utf-8 -*-
# © 2014 Acsone SA/NV (http://www.acsone.eu)
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.addons.stock.tests.common import TestStockCommon


class StockInventoryLocationTest(TestStockCommon):
    def setUp(self):
        super(StockInventoryLocationTest, self).setUp()
        # Make a new location
        self.new_location = self.env['stock.location'].create(
            {'name': 'Test location',
             'usage': 'internal'})
        self.new_sublocation = self.env['stock.location'].create(
            {'name': 'Test sublocation',
             'usage': 'internal',
             'location_id': self.new_location.id})
        # Input goods
        self.env['stock.quant'].create(
            {'location_id': self.new_location.id,
             'product_id': self.productA.id,
             'qty': 10.0})
        # Prepare an inventory
        self.inventory = self.env['stock.inventory'].create(
            {'name': 'Lock down location',
             'filter': 'none',
             'location_id': self.new_location.id})
        self.inventory.prepare_inventory()
        self.assertTrue(self.inventory.line_ids, 'The inventory is empty.')

    def test_update_parent_location(self):
        """Updating the parent of a location is OK if no inv. in progress."""
        self.inventory.action_cancel_draft()
        self.inventory.location_id.location_id = self.env.ref(
            'stock.stock_location_4')

    def test_update_parent_location_locked_down(self):
        """Updating the parent of a location must fail"""
        with self.assertRaises(ValidationError):
            self.inventory.location_id.location_id = self.env.ref(
                'stock.stock_location_4')

    def test_inventory(self):
        """We must still be able to finish the inventory"""
        self.assertTrue(self.inventory.line_ids)
        self.inventory.line_ids.write({'product_qty': 42.0})
        for line in self.inventory.line_ids:
            self.assertNotEqual(line.product_id.with_context(
                location=line.location_id.id).qty_available, 42.0)
        self.inventory.action_done()
        for line in self.inventory.line_ids:
            self.assertEqual(line.product_id.with_context(
                location=line.location_id.id).qty_available, 42.0)

    def test_inventory_sublocation(self):
        """We must be able to make an inventory in a sublocation"""
        inventory_subloc = self.env['stock.inventory'].create(
            {'name': 'Lock down location',
             'filter': 'partial',
             'location_id': self.new_sublocation.id})
        inventory_subloc.prepare_inventory()
        line = self.env['stock.inventory.line'].create(
            {'product_id': self.productA.id,
             'product_qty': 22.0,
             'location_id': self.new_sublocation.id,
             'inventory_id': inventory_subloc.id})
        self.assertTrue(inventory_subloc.line_ids)
        inventory_subloc.action_done()
        self.assertEqual(line.product_id.with_context(
            location=line.location_id.id).qty_available, 22.0)

    def test_move(self):
        """Stock move must be forbidden during inventory"""
        move = self.env['stock.move'].create({
            'name': 'Test move lock down',
            'product_id': self.productA.id,
            'product_uom_qty': 10.0,
            'product_uom': self.productA.uom_id.id,
            'location_id': self.inventory.location_id.id,
            'location_dest_id': self.customer_location
            })
        with self.assertRaises(ValidationError):
            move.action_done()
