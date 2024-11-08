# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests.common import TransactionCase


class TestStockLocationChildren(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        ref = cls.env.ref
        cls.stock_input = ref("stock.stock_location_company")
        cls.stock_location = ref("stock.stock_location_stock")
        cls.test_location = cls.env["stock.location"].create(
            {"name": "Test Location", "location_id": cls.stock_location.id}
        )
        cls.stock_shelf_1 = cls.env["stock.location"].create(
            {"name": "Test Shelf 1", "location_id": cls.test_location.id}
        )
        cls.stock_shelf_2 = cls.env["stock.location"].create(
            {"name": "Test Shelf 2", "location_id": cls.test_location.id}
        )
        cls.stock_shelf_2_refrigerator = cls.env["stock.location"].create(
            {"name": "Test Shelf Refrigerator", "location_id": cls.stock_shelf_2.id}
        )

    def test_location_children(self):
        self.assertFalse(self.stock_shelf_2_refrigerator.child_ids)
        self.assertEqual(self.stock_shelf_2.child_ids, self.stock_shelf_2_refrigerator)
        self.assertEqual(self.stock_shelf_2.child_ids, self.stock_shelf_2.children_ids)
        self.assertFalse(self.stock_shelf_1.child_ids)
        self.assertFalse(self.stock_shelf_1.children_ids)
        self.assertEqual(
            self.test_location.child_ids, self.stock_shelf_1 | self.stock_shelf_2
        )
        self.assertEqual(
            self.test_location.children_ids,
            self.stock_shelf_1 | self.stock_shelf_2 | self.stock_shelf_2_refrigerator,
        )

    def test_create_write_location(self):
        refrigerator_drawer = self.env["stock.location"].create(
            {
                "name": "Refrigerator drawer",
                "location_id": self.stock_shelf_2_refrigerator.id,
            }
        )
        self.assertEqual(self.stock_shelf_2_refrigerator.child_ids, refrigerator_drawer)
        self.assertEqual(
            self.stock_shelf_2_refrigerator.children_ids, refrigerator_drawer
        )
        self.assertEqual(
            self.stock_shelf_2.children_ids,
            self.stock_shelf_2_refrigerator | refrigerator_drawer,
        )
        self.assertEqual(
            self.test_location.children_ids,
            self.stock_shelf_1
            | self.stock_shelf_2
            | self.stock_shelf_2_refrigerator
            | refrigerator_drawer,
        )
        refrigerator_drawer.location_id = self.stock_input
        self.assertFalse(self.stock_shelf_2_refrigerator.child_ids)
        self.assertEqual(self.stock_shelf_2.child_ids, self.stock_shelf_2_refrigerator)
        self.assertEqual(self.stock_shelf_2.child_ids, self.stock_shelf_2.children_ids)
        self.assertNotIn(
            self.stock_shelf_2_refrigerator.children_ids, refrigerator_drawer
        )
        self.assertEqual(
            self.test_location.children_ids,
            self.stock_shelf_1 | self.stock_shelf_2 | self.stock_shelf_2_refrigerator,
        )
