# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests.common import TransactionCase


class TestStockLocation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_7")
        cls.leaf_location = cls.env.ref("stock.location_refrigerator_small")
        cls.top_location = cls.leaf_location.location_id

    def _create_user(self, name, groups):
        return (
            self.env["res.users"]
            .with_context(**{"no_reset_password": True})
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

    def test_leaf_location(self):
        self.assertFalse(self.leaf_location.child_ids)
        inventory = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.leaf_location.id,
                "inventory_quantity": 5,
            }
        )
        inventory.action_apply_inventory()
        self.assertNotEqual(
            self.leaf_location.last_inventory_date, inventory.inventory_date
        )

    def test_top_location(self):
        inventory = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.leaf_location.id,
                "inventory_quantity": 5,
            }
        )
        inventory.action_apply_inventory()
        self.assertNotEqual(
            self.leaf_location.last_inventory_date, inventory.inventory_date
        )
        self.assertNotEqual(
            self.top_location.last_inventory_date, inventory.inventory_date
        )
