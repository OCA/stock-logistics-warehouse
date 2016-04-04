# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp.tests.common import SavepointCase
from openerp.exceptions import ValidationError

from ..models.stock_inventory import CONSISTANT_STATES

_logger = logging.getLogger(__name__)

# How many levels of sub-locations in the test data (must be >= 2)
MAX_DEPTH = 4
# How many children in each location
NB_SUB_LOCS = 4
# Every how many levels we put internal locations
STRIDE_INTERNAL = 2
# Every how many locations we put quants
STRIDE_QUANTS = 2


class TestHierarchicalInventory(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """Set up a large warehouse, representative of the module use-case"""
        super(TestHierarchicalInventory, cls).setUpClass()
        main_company_id = cls.env.ref('base.main_company').id
        defered_loc_obj = cls.env['stock.location'].with_context(
            defer_parent_store_computation=True)
        # Create 1 main location
        cls.main_location_id = defered_loc_obj.create(
            {'name': 'Main location',
             'company_id': main_company_id,
             'location_id': cls.env.ref("stock.stock_location_stock").id,
             'usage': 'view'})

        locations = [cls.main_location_id]
        product_id = cls.env.ref('product.product_product_10').id
        cls.nb_quants = 0
        cls.nb_locations = {'internal': 0, 'view': 0}
        for depth in range(MAX_DEPTH):
            _logger.info("Creating the locations at depth %d" % depth)
            new_locations = []
            for location in locations:
                # Create sub-locations in each location
                for n in range(NB_SUB_LOCS):
                    new_loc = defered_loc_obj.create(
                        {'name': '%s-%d' % (location.name, n),
                         'location_id': location.id,
                         'company_id': main_company_id,
                         'usage': ((depth % STRIDE_INTERNAL) and 'internal' or
                                   'view')})
                    cls.nb_locations[new_loc.usage] += 1
                    new_locations.append(new_loc)
                    # Create quants in some locations
                    if new_loc.usage == 'internal' and (n % STRIDE_QUANTS):
                        cls.env['stock.quant'].create(
                            {'location_id': new_loc.id,
                             'company_id': main_company_id,
                             'product_id': product_id,
                             'qty': 10.0})
                        cls.nb_quants += 1
            locations = new_locations
        defered_loc_obj._parent_store_compute()

    def _call_wizard(self, level, only_view=False):
        """Call the wizard to create the inventory hierarchy

        @return: main inventory record"""
        wizard = self.env['stock.generate.inventory'].create(
            {'prefix_inv_name': 'TEST-',
             'location_id': self.main_location_id.id,
             'level': level,
             'only_view': only_view})
        view = wizard.generate_inventory()
        return self.env['stock.inventory'].browse(view['res_id'])

    def test_recursion(self):
        # Putting an inventory inside one of it's children must fail
        main_inv = self._call_wizard(2, only_view=True)
        with self.assertRaises(ValidationError):
            main_inv.parent_id = main_inv.inventory_ids[0]

    def test_states(self):
        """Parent and children states must be consistent"""
        main_inv = self._call_wizard(MAX_DEPTH + 1, only_view=True)
        children = self.env['stock.inventory'].search(
            [('parent_id', 'child_of', main_inv.id),
             ('id', '!=', main_inv.id)])
        self.assertTrue(children, "No sub-inventories were created")

        # key: parent state, value: consistent children states
        for parent_state, ok_states in CONSISTANT_STATES.items():
            # try to change the parent (and children) to a state
            (main_inv | children).write({'state': parent_state})
            for child_state in ['draft', 'confirm', 'done', 'cancel']:
                if child_state in ok_states:
                    # It must be possible to change the children to this state
                    children.write({'state': child_state})
                else:
                    # Changing the children to this state must fail
                    with self.assertRaises(ValidationError):
                        children.write({'state': child_state})

    def test_complete_name(self):
        """The complete name must contain the parent's name"""
        main_inv = self._call_wizard(2)
        self.assertTrue(main_inv.inventory_ids,
                        "No sub-inventories were created")
        for inventory in main_inv.inventory_ids:
            self.assertEqual(inventory.complete_name,
                             main_inv.name + ' / ' + inventory.name)

    def test_wizard(self):
        """Check the wizard makes a correct hierarchy"""
        # Check with a hierarchy based on all locations
        main_inv = self._call_wizard(MAX_DEPTH + 1, only_view=False)
        self.assertEqual(len(main_inv.inventory_ids), NB_SUB_LOCS)
        children = self.env['stock.inventory'].search(
            [('parent_id', 'child_of', main_inv.id),
             ('id', '!=', main_inv.id)])
        self.assertEqual(
            len(children),
            self.nb_locations['view'] + self.nb_locations['internal'])

        # Check with a hierarchy based on views only
        main_inv = self._call_wizard(MAX_DEPTH + 1, only_view=True)
        children = self.env['stock.inventory'].search(
            [('parent_id', 'child_of', main_inv.id),
             ('id', '!=', main_inv.id)])
        self.assertEqual(len(main_inv.inventory_ids), NB_SUB_LOCS)
        self.assertEqual(
            len(children),
            self.nb_locations['view'])

    def test_prepare_standard(self):
        """Preparing a standard inventory must still work"""
        inv = self.env['stock.inventory'].create(
            {'name': 'Test',
             'filter': 'none',
             'location_id': self.main_location_id.id})
        self.assertFalse(inv.inventory_ids, "Sub-inventories were created")
        inv.prepare_inventory()
        for line in inv.line_ids:
            self.assertEqual(line.product_qty, 10.0)
        self.assertEqual(
            len(inv.line_ids),
            self.nb_quants)
        # check we can change the quantities (set to 0)
        inv.reset_real_qty()
        inv.action_done()

    def test_prepare_hierarchy(self):
        """Preparing the parent should prepare all the children"""
        main_inv = self._call_wizard(MAX_DEPTH + 1, only_view=True)
        main_inv.prepare_inventory()
        children = self.env['stock.inventory'].search(
            [('id', 'child_of', main_inv.id), ('id', '!=', main_inv.id)])
        for child in children:
            self.assertTrue(child.line_ids, "%s has no lines" % child.name)
            self.assertEqual(child.state, 'confirm', "Child: %s" % child.name)

    def test_action_done_hierarchy(self):
        """Test the inventory can be done"""
        main_inv = self._call_wizard(3, only_view=True)
        main_inv.prepare_inventory()
        for inventories in [main_inv.inventory_ids.mapped("inventory_ids"),
                            main_inv.inventory_ids,
                            main_inv]:
            for line in inventories.mapped("line_ids"):
                line.product_qty = 24.0
                self.assertEqual(line.product_qty, 24.0)
            for inventory in inventories:
                inventory.action_done()

    def test_children_dates(self):
        """Children should all have the same dates as their parents"""
        main_inv = self._call_wizard(MAX_DEPTH + 1, only_view=True)
        children = self.env['stock.inventory'].search(
            [('parent_id', 'child_of', main_inv.id)])
        main_inv.prepare_inventory()
        for child in children:
            self.assertEqual(child.date, main_inv.date,
                             "Child: %s" % child.name)

    def test_cancel(self):
        """Children must be canceled (draft) when the parent is canceled."""
        main_inv = self._call_wizard(MAX_DEPTH + 1, only_view=True)
        children = self.env['stock.inventory'].search(
            [('parent_id', 'child_of', main_inv.id)])
        main_inv.prepare_inventory()
        main_inv.action_cancel_inventory()
        for child in children:
            self.assertEqual(child.state, "draft",
                             "Child: %s" % child.name)
