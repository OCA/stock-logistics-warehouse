# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.stock_inventory_hierarchical.\
    tests.test_hierarchical_inventory \
    import TestHierarchicalInventory, MAX_DEPTH


class TestHierarchicalExhaustiveInventory(TestHierarchicalInventory):

    def _call_wizard(self, level, only_view=False, exhaustive=True):
        """Call the wizard to create the inventory exhaustive hierarchy

        @return: main inventory record"""
        wizard = self.env['stock.generate.inventory'].create(
            {'prefix_inv_name': 'TEST_EXHAUSTIVE-',
             'location_id': self.main_location_id.id,
             'level': level,
             'only_view': only_view,
             'exhaustive': exhaustive})
        view = wizard.generate_inventory()
        return self.env['stock.inventory'].browse(view['res_id'])

    def test_wizard_exhaustive(self):
        """The wizard must create exhaustive inventories when demanded"""
        for exhaustive in [True, False]:
            main_inv = self._call_wizard(MAX_DEPTH + 1, exhaustive=exhaustive)
            for inventory in self.env['stock.inventory'].search(
                    [('id', 'child_of', main_inv.id)]):
                self.assertEqual(inventory.exhaustive, exhaustive)

    def test_missing_locations(self):
        """Locations of sub inventories must not be reported missing"""
        main_inv = self._call_wizard(MAX_DEPTH + 1)
        main_inv.prepare_inventory()
        missing_locations = main_inv.get_missing_locations()
        self.assertFalse(missing_locations)

    def test_exhaustive_propagation(self):
        """Checking exhaustive on the parent must propagate to the children"""
        main_inv = self._call_wizard(MAX_DEPTH + 1)
        for inventory in self.env['stock.inventory'].search(
                [('id', 'child_of', main_inv.id)]):
            self.assertTrue(inventory.exhaustive)

        main_inv.exhaustive = False
        for inventory in self.env['stock.inventory'].search(
                [('id', 'child_of', main_inv.id)]):
            self.assertFalse(inventory.exhaustive)
