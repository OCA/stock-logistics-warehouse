# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import SavepointCase


class TestStockLocation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_7")
        cls.leaf_location = cls.env.ref("stock.location_refrigerator_small")
        cls.top_location = cls.leaf_location.location_id

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
