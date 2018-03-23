# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.stock.tests.common import TestStockCommon


class TestExhaustiveInventory(TestStockCommon):
    def setUp(self):
        super(TestExhaustiveInventory, self).setUp()
        # Empty location
        self.location = self.env['stock.location'].create(
            {'name': 'test location'})
        # Force-enter quants to simulate goods in stock
        for p in [self.productA, self.productB, self.productC]:
            self.env["stock.quant"].create(
                {'product_id': p.id,
                 'qty': 42.0,
                 'location_id': self.location.id})

        # Create an exhaustive inventory
        self.inventory = self.env["stock.inventory"].create(
            {'name': 'Standard inventory',
             'location_id': self.location.id,
             'filter': 'partial',
             'exhaustive': True})
        self._assert_quantities(42.0, 42.0, 42.0)

    def _add_lines(self):
        """Add 2 test lines

        All locations are included, but only 2 products out of 3 are."""
        self.env["stock.inventory.line"].create(
            {'product_id': self.productA.id,
             'product_uom': self.productA.uom_id.id,
             'inventory_id': self.inventory.id,
             'product_qty': 18.0,
             'location_id': self.location.id})
        self.env["stock.inventory.line"].create(
            {'product_id': self.productB.id,
             'product_uom': self.productB.uom_id.id,
             'inventory_id': self.inventory.id,
             'product_qty': 12.0,
             'location_id': self.location.id})

    def _assert_quantities(self, qtyA, qtyB, qtyC):
        """Assert the quantities of the 3 products"""
        self.assertEqual(
            self.productA.with_context(
                location=self.location.id).qty_available,
            qtyA)
        self.assertEqual(
            self.productB.with_context(
                location=self.location.id).qty_available,
            qtyB)
        self.assertEqual(
            self.productC.with_context(
                location=self.location.id).qty_available,
            qtyC)

    def test_get_missing_locations(self):
        """Get_missing_locations must return the uninventoried locations"""
        self.inventory.prepare_inventory()
        self.assertEqual(self.inventory.state, 'confirm')
        self.assertEqual(len(self.inventory.get_missing_locations()), 1)
        self._add_lines()
        self.assertEqual(len(self.inventory.get_missing_locations()), 0)

    def test_confirm_missing_locations(self):
        """confirm_missing_locations returns an action if locations missing"""
        # If a location is missing, we get an action dictionary
        action = self.inventory.confirm_missing_locations()
        self.assertIsInstance(action, dict)
        # Otherwise it returns True and does the inventory
        self._add_lines()
        self.inventory.confirm_missing_locations()
        self.assertEquals(self.inventory.state, 'done')
        # Check the inventory zeroed out productC
        self._assert_quantities(18.0, 12.0, 0.0)

    def test_action_done(self):
        """action_done must zero out the missing products"""
        self.inventory.prepare_inventory()
        self.assertEqual(self.inventory.state, 'confirm')
        self._add_lines()
        self.inventory.action_done()
        self.assertEquals(self.inventory.state, 'done')
        self._assert_quantities(18.0, 12.0, 0.0)

    def test_confirmation_wizard(self):
        """The wizard must contain a list of uninventoried locations"""
        self.inventory.prepare_inventory()
        self.assertEqual(self.inventory.state, 'confirm')
        wiz = self.env['stock.inventory.uninventoried.locations'].with_context(
            active_ids=[self.inventory.id]).create({})
        self.assertEqual(len(wiz.location_ids), 1)

        # Confirming the missing locations creates inventory lines with qty=0
        wiz.confirm_uninventoried_locations()
        self.assertEquals(self.inventory.state, 'done')
        self._assert_quantities(0.0, 0.0, 0.0)

    def test_standard_inventory(self):
        """Standard inventories must work as usual"""
        self.inventory.exhaustive = False
        self.inventory.prepare_inventory()
        self.assertEqual(self.inventory.state, 'confirm')
        self._add_lines()
        self.assertEqual(len(self.inventory.line_ids), 2)
        self.inventory.action_done()
        self.assertEqual(self.inventory.state, 'done')
        self._assert_quantities(18.0, 12.0, 42.0)

    def test_exhaustive_filter(self):
        """By definition, exhaustive implies the filter "all products"."""
        self.inventory.exhaustive = False
        self.inventory.filter = 'product'
        self.inventory.exhaustive = True
        # Simulate the client change reaction
        self.inventory._onchange_exhaustive()
        self.assertEqual(self.inventory.filter, 'none')
