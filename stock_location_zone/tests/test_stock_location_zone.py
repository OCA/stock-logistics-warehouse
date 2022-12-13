# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockLocationZone(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.location_obj = cls.env["stock.location"]
        # Create the following structure:
        # # [Zone Location]
        # # # [Area Location]
        # # # # [Bin Location]
        cls.location_zone = cls.location_obj.create(
            {
                "name": "Zone Location",
                "is_zone": True,
            }
        )
        cls.location_area = cls.location_obj.create(
            {"name": "Area Location", "location_id": cls.location_zone.id}
        )
        cls.location_bin = cls.location_obj.create(
            {"name": "Bin Location", "location_id": cls.location_area.id}
        )
        cls.scrap_location = cls.location_obj.create(
            {
                "name": "Scrap Location",
                "usage": "inventory",
            }
        )
        cls.stock_location = cls.env.ref("stock.warehouse0").lot_stock_id

    def test_location_kind(self):
        self.assertEqual("zone", self.location_zone.location_kind)
        self.assertEqual("area", self.location_area.location_kind)
        self.assertEqual("bin", self.location_bin.location_kind)
        self.assertEqual("stock", self.stock_location.location_kind)
        self.assertEqual("other", self.scrap_location.location_kind)

    def test_location_zone(self):
        # Check that Zone Location has:
        # # The zone location as self
        # # No area location
        self.assertEqual(
            self.location_zone.zone_location_id,
            self.location_zone,
        )
        self.assertFalse(self.location_zone.area_location_id)
        # Check that Area Location has:
        # # The zone location is Zone Location
        # # The area location is self
        self.assertEqual(self.location_zone, self.location_area.zone_location_id)
        self.assertEqual(self.location_area, self.location_area.area_location_id)
        # Check the Bin Location
        # # The zone location is Zone Location
        # # The area location is Area Location
        self.assertEqual(self.location_zone, self.location_bin.zone_location_id)
        self.assertEqual(self.location_area, self.location_bin.area_location_id)
