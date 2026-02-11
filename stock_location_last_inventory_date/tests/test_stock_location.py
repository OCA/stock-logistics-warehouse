# Copyright 2021 Camptocamp SA
# Copyright 2024 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import SavepointCase


class TestStockLocation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_7")
        cls.top_location = cls.env["stock.location"].create(
            {
                "name": "Top",
                "location_id": cls.env.ref("stock.stock_location_locations").id,
            }
        )
        cls.leaf_location = cls.env["stock.location"].create(
            {"name": "Leaf", "location_id": cls.top_location.id}
        )
        cls.test_locations = cls.top_location | cls.leaf_location
        cls.env["stock.quant"]._update_available_quantity(
            cls.product,
            cls.top_location,
            10,
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product,
            cls.leaf_location,
            10,
        )

    def _create_user(self, name, groups):
        return (
            self.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": name.capitalize(),
                    "password": "password",
                    "login": name,
                    "email": "{}@test.com".format(name.lower()),
                    "groups_id": [(6, 0, groups.ids)],
                    "company_ids": [(6, 0, self.env["res.company"].search([]).ids)],
                }
            )
        )

    def test_leaf_location_non_privileged_user(self):
        stock_user = self._create_user(
            "Stock Normal", self.env.ref("stock.group_stock_user")
        )
        stock_manager = self._create_user(
            "Stock Admin", self.env.ref("stock.group_stock_manager")
        )
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Inventory Adjustment",
                "product_ids": [(4, self.product.id)],
                "location_ids": [(4, self.leaf_location.id)],
            }
        )
        inventory.with_user(stock_user).action_start()
        inventory.with_user(stock_manager).action_validate()
        self.assertEqual(
            self.leaf_location.with_user(stock_user).last_inventory_date, inventory.date
        )
        try:
            # Triggers the computation indirectly, `date` is in the depends.
            inventory.with_user(stock_user).date = fields.Datetime.now()
        except AccessError:
            self.fail("A non-privileged user could not trigger the recomputation.")

    def test_leaf_location(self):
        self.assertFalse(self.leaf_location.child_ids)
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Inventory Adjustment",
                "product_ids": [(4, self.product.id)],
                "location_ids": [(4, self.leaf_location.id)],
            }
        )
        inventory.action_start()
        inventory.action_validate()
        self.assertEqual(self.leaf_location.last_inventory_date, inventory.date)
        self.assertFalse(self.top_location.last_inventory_date)
        locations = self.env["stock.location"].search(
            [
                ("last_inventory_date", "<=", inventory.date),
                ("id", "in", self.test_locations.ids),
            ]
        )
        self.assertEqual(locations, self.leaf_location)

    def test_top_location(self):
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Inventory Adjustment",
                "product_ids": [(4, self.product.id)],
                "location_ids": [(4, self.top_location.id)],
            }
        )
        inventory.action_start()
        inventory.action_validate()
        self.assertEqual(self.leaf_location.last_inventory_date, inventory.date)
        self.assertEqual(self.top_location.last_inventory_date, inventory.date)
        locations = self.env["stock.location"].search(
            [
                ("last_inventory_date", "<=", inventory.date),
                ("id", "in", self.test_locations.ids),
            ]
        )
        self.assertEqual(locations, self.test_locations)

    def test_top_and_leaf_location(self):
        self.test_top_location()
        top_inventory_date = self.top_location.last_inventory_date
        with freeze_time(fields.Date.add(top_inventory_date, days=5)):
            inventory = self.env["stock.inventory"].create(
                {
                    "name": "Inventory Adjustment",
                    "product_ids": [(4, self.product.id)],
                    "location_ids": [(4, self.leaf_location.id)],
                }
            )
            inventory.action_start()
            inventory.action_validate()
        leaf_inventory_date = self.leaf_location.last_inventory_date
        self.assertTrue(leaf_inventory_date > top_inventory_date)
        locations = self.env["stock.location"].search(
            [
                ("last_inventory_date", "<=", leaf_inventory_date),
                ("id", "in", self.test_locations.ids),
            ]
        )
        self.assertEqual(locations, (self.leaf_location | self.top_location))
        locations = self.env["stock.location"].search(
            [
                ("last_inventory_date", "<=", top_inventory_date),
                ("id", "in", self.test_locations.ids),
            ]
        )
        self.assertEqual(locations, self.top_location)

    def test_empty_location(self):
        empty_location = self.env["stock.location"].create(
            {"name": "Leaf", "location_id": self.top_location.id}
        )
        leaf_empty_location = self.env["stock.location"].create(
            {"name": "Leaf", "location_id": empty_location.id}
        )
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Inventory Adjustment",
                "location_ids": [(4, empty_location.id)],
            }
        )
        inventory.action_start()
        inventory.action_validate()
        self.assertEqual(empty_location.last_inventory_date, inventory.date)
        self.assertEqual(leaf_empty_location.last_inventory_date, inventory.date)
        self.assertFalse(self.top_location.last_inventory_date)

    def test_inventory_nochange_location(self):

        inventory = self.env["stock.inventory"].create(
            {
                "name": "Inventory Adjustment",
                "product_ids": [(4, self.product.id)],
                "location_ids": [(4, self.leaf_location.id)],
            }
        )
        inventory.action_start()
        inventory.action_validate()
        self.assertEqual(self.leaf_location.last_inventory_date, inventory.date)
        self.assertFalse(self.top_location.last_inventory_date)

        new_inventory_date = fields.Date.add(inventory.date, days=10)
        string_inventory_date = fields.Datetime.to_string(new_inventory_date)

        with freeze_time(string_inventory_date):
            inventory = self.env["stock.inventory"].create(
                {
                    "name": "Inventory Adjustment",
                    "product_ids": [(4, self.product.id)],
                    "location_ids": [(4, self.leaf_location.id)],
                }
            )
            inventory.action_start()
            inventory.action_validate()
            self.assertEqual(self.leaf_location.last_inventory_date, inventory.date)
            self.assertFalse(self.top_location.last_inventory_date)
