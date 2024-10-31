# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestChildLocation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location_obj = cls.env["stock.location"]
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.product_obj = cls.env["product.product"]

        # Create Locations structure
        cls.large_shelves = cls.location_obj.create(
            {
                "name": "Large Shelves",
                "location_id": cls.stock.id,
                "usage": "view",
            }
        )

        cls.large_shelf_1 = cls.location_obj.create(
            {
                "name": "Large Shelf 1",
                "location_id": cls.large_shelves.id,
                "usage": "internal",
            }
        )
        cls.large_shelf_2 = cls.location_obj.create(
            {
                "name": "Large Shelf 2",
                "location_id": cls.large_shelves.id,
                "usage": "internal",
            }
        )
        cls.large_shelf_3 = cls.location_obj.create(
            {
                "name": "Large Shelf 3",
                "location_id": cls.large_shelves.id,
                "usage": "internal",
            }
        )

        cls.medium_shelves = cls.location_obj.create(
            {
                "name": "Medium Shelves",
                "location_id": cls.stock.id,
                "usage": "view",
            }
        )

        cls.medium_shelf_1 = cls.location_obj.create(
            {
                "name": "Medium Shelf 1",
                "location_id": cls.medium_shelves.id,
                "usage": "internal",
            }
        )
        cls.medium_shelf_2 = cls.location_obj.create(
            {
                "name": "Medium Shelf 2",
                "location_id": cls.medium_shelves.id,
                "usage": "internal",
            }
        )
        cls.medium_shelf_3 = cls.location_obj.create(
            {
                "name": "Medium Shelf 3",
                "location_id": cls.medium_shelves.id,
                "usage": "internal",
            }
        )

        cls.tiny_shelves = cls.location_obj.create(
            {
                "name": "Tiny Shelves",
                "location_id": cls.stock.id,
                "usage": "view",
            }
        )

        cls.black_tiny_shelves = cls.location_obj.create(
            {
                "name": "Black Tiny Shelves",
                "location_id": cls.tiny_shelves.id,
                "usage": "view",
            }
        )

        cls.black_tiny_shelf_1 = cls.location_obj.create(
            {
                "name": "Black Tiny Shelf 1",
                "location_id": cls.black_tiny_shelves.id,
                "usage": "internal",
            }
        )
        cls.black_tiny_shelf_2 = cls.location_obj.create(
            {
                "name": "Black Tiny Shelf 2",
                "location_id": cls.black_tiny_shelves.id,
                "usage": "internal",
            }
        )
        cls.black_tiny_shelf_3 = cls.location_obj.create(
            {
                "name": "Black Tiny Shelf 3",
                "location_id": cls.black_tiny_shelves.id,
                "usage": "internal",
            }
        )

        cls.white_tiny_shelves = cls.location_obj.create(
            {
                "name": "White Tiny Shelves",
                "location_id": cls.tiny_shelves.id,
                "usage": "view",
            }
        )

        cls.white_tiny_shelf_1 = cls.location_obj.create(
            {
                "name": "White Tiny Shelf 1",
                "location_id": cls.white_tiny_shelves.id,
                "usage": "internal",
            }
        )
        cls.white_tiny_shelf_2 = cls.location_obj.create(
            {
                "name": "White Tiny Shelf 2",
                "location_id": cls.white_tiny_shelves.id,
                "usage": "internal",
            }
        )
        cls.white_tiny_shelf_3 = cls.location_obj.create(
            {
                "name": "White Tiny Shelf 3",
                "location_id": cls.white_tiny_shelves.id,
                "usage": "internal",
            }
        )

    def test_child_location(self):
        # Check that the root location contains all expected elements (just children)
        self.assertEqual(
            self.large_shelves.children_location_ids,
            (self.large_shelf_1 | self.large_shelf_2 | self.large_shelf_3),
        )
        self.large_shelf_1.location_id = self.medium_shelves
        self.large_shelves.invalidate_recordset()
        self.assertEqual(
            self.large_shelves.children_location_ids,
            (self.large_shelf_2 | self.large_shelf_3),
        )

        self.assertEqual(
            self.tiny_shelves.children_location_ids,
            (
                self.black_tiny_shelves
                | self.black_tiny_shelf_1
                | self.black_tiny_shelf_2
                | self.black_tiny_shelf_3
                | self.white_tiny_shelves
                | self.white_tiny_shelf_1
                | self.white_tiny_shelf_2
                | self.white_tiny_shelf_3
            ),
        )

    def test_action(self):
        # Check the action to view all children
        action = self.large_shelves.action_show_children_locations()
        self.assertDictContainsSubset(
            {"domain": [("id", "in", self.large_shelves.children_location_ids.ids)]},
            action,
        )
