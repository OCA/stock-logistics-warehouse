# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase


class TestStockLocation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_7")
        cls.leaf_location = cls.env.ref("stock.location_refrigerator_small")
        cls.top_location = cls.leaf_location.location_id

    def test_leaf_location(self):
        self.assertFalse(self.leaf_location.child_ids)
        self.assertFalse(self.leaf_location.validated_inventory_ids)
        self.assertFalse(self.leaf_location.last_inventory_date)
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Inventory Adjustment",
                "product_ids": [(4, self.product.id)],
                "location_ids": [(4, self.leaf_location.id)],
            }
        )
        inventory.action_start()
        inventory.action_validate()
        self.assertEqual(self.leaf_location.validated_inventory_ids.ids, [inventory.id])
        self.assertEqual(self.leaf_location.last_inventory_date, inventory.date)

    def test_top_location(self):
        self.assertTrue(self.top_location.child_ids)
        self.assertFalse(self.top_location.validated_inventory_ids)
        self.assertFalse(self.top_location.last_inventory_date)
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Inventory Adjustment",
                "product_ids": [(4, self.product.id)],
                "location_ids": [(4, self.top_location.id)],
            }
        )
        inventory.action_start()
        inventory.action_validate()
        self.assertEqual(self.top_location.validated_inventory_ids.ids, [inventory.id])
        self.assertFalse(self.top_location.last_inventory_date)
