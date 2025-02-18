# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestStockLocationPosition(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "Test Warehouse", "code": "TST"}
        )
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Test Location",
                "corridor": "A",
                "row": "1",
                "rack": "2",
                "level": "3",
                "posx": 10,
                "posy": 20,
                "posz": 30,
                "usage": "internal",
            }
        )

    def test_location_position_creation(self):
        """Test the creation of a location with position fields"""
        self.assertEqual(self.location.corridor, "A")
        self.assertEqual(self.location.row, "1")
        self.assertEqual(self.location.rack, "2")
        self.assertEqual(self.location.level, "3")
        self.assertEqual(self.location.posx, 10)
        self.assertEqual(self.location.posy, 20)
        self.assertEqual(self.location.posz, 30)

    def test_location_search(self):
        """Test searching locations by position fields"""
        locations = self.env["stock.location"].search(
            [
                ("corridor", "=", "A"),
                ("row", "=", "1"),
                ("level", "=", "3"),
            ]
        )
        self.assertIn(self.location, locations)

        locations = self.env["stock.location"].search(
            [
                ("posx", "=", 10),
                ("posy", "=", 20),
                ("posz", "=", 30),
            ]
        )
        self.assertIn(self.location, locations)
