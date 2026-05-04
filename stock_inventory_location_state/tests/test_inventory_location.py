# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockInventoryLocationState(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.stock_location = cls.env.ref("stock.warehouse0").lot_stock_id
        cls.shelf_loc = cls.env["stock.location"].create(
            {"name": "SHELF", "location_id": cls.stock_location.id}
        )
        cls.child1_loc = cls.env["stock.location"].create(
            {"name": "DRAWER_1", "location_id": cls.shelf_loc.id}
        )
        cls.child2_loc = cls.env["stock.location"].create(
            {"name": "DRAWER_2", "location_id": cls.shelf_loc.id}
        )
        cls.sub_locations = cls.shelf_loc | cls.child1_loc | cls.child2_loc
        cls.product = cls.env["product.product"].create(
            {"name": "Test", "is_storable": True}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.child1_loc, 1
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.child2_loc, 1
        )

    def test_inventory_location_flow(self):
        inventory = self.env["stock.inventory"].create(
            {"location_ids": [Command.set(self.shelf_loc.ids)]}
        )
        self.assertFalse(inventory.sub_location_ids)
        inventory.action_state_to_in_progress()
        self.assertEqual(inventory.sub_location_ids.location_id, self.sub_locations)
        inventory.sub_location_ids[0].action_start()
        inventory.sub_location_ids[0].action_done()
        self.assertEqual(inventory.location_count, len(self.sub_locations))
        self.assertEqual(inventory.done_location_count, 1)
        self.assertEqual(
            inventory.remaining_location_count, len(self.sub_locations) - 1
        )
        with self.assertRaises(UserError):
            inventory.action_state_to_done()
        inventory.sub_location_ids.write({"state": "done"})
        inventory.action_state_to_done()

    def test_inactive_child(self):
        location = self.env["stock.location"].create(
            {
                "name": "No more child",
                "usage": "internal",
            }
        )
        self.env["stock.location"].create(
            {
                "location_id": location.id,
                "name": "Inactive Child",
                "usage": "internal",
                "active": False,
            }
        )
        inventory = self.env["stock.inventory"].create(
            {"location_ids": [Command.set(location.ids)]}
        )
        inventory.action_state_to_in_progress()
        self.assertEqual(inventory.location_count, 1)
        self.assertEqual(inventory.sub_location_ids.location_id, location)

    def test_inventory_location_actions(self):
        inventory = self.env["stock.inventory"].create(
            {"location_ids": [Command.set(self.shelf_loc.ids)]}
        )
        self.assertFalse(inventory.sub_location_ids)
        inventory.action_state_to_in_progress()
        inventory_location = inventory.sub_location_ids[0]
        self.assertTrue(inventory_location)
        with self.assertRaises(UserError):
            inventory_location.action_done()
        inventory_location.action_start()
        self.assertEqual(inventory_location.state, "started")
        inventory_location.action_reopen()
        self.assertEqual(inventory_location.state, "pending")
        inventory_location.action_start()
        inventory_location.action_done()
        with self.assertRaises(UserError):
            inventory_location.action_start()
