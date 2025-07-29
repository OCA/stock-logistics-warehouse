# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TrayTypeCommonCase


class TestTrayType(TrayTypeCommonCase):
    def test_tray_type_write_sync(self):
        # both tray 1A and tray 2D use stock_location_tray_type_small_8x
        tray_type = self.env.ref(
            "stock_location_tray.stock_location_tray_type_small_8x"
        )

        tray_type.write({"storage_category_id": self.location_category_buffer})

        self.assertEqual(
            self.location_1a.storage_category_id, self.location_category_buffer
        )
        self.assertEqual(
            self.location_2d.storage_category_id, self.location_category_buffer
        )

    def test_location_create_sync(self):
        # both tray 1A and tray 2D use stock_location_tray_type_small_8x
        tray_type = self.env.ref(
            "stock_location_tray.stock_location_tray_type_small_8x"
        )
        tray_type.write({"storage_category_id": self.location_category_buffer})

        locations = self.location_2a | self.location_2b

        self.assertNotEqual(
            self.location_2a.storage_category_id, self.location_category_buffer
        )
        self.assertNotEqual(
            self.location_2b.storage_category_id, self.location_category_buffer
        )

        locations.tray_type_id = tray_type

        self.assertEqual(
            self.location_2a.storage_category_id, self.location_category_buffer
        )
        self.assertEqual(
            self.location_2b.storage_category_id, self.location_category_buffer
        )
