# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TrayTypeCommonCase


class TestTrayType(TrayTypeCommonCase):
    def test_tray_type_write_sync(self):
        # both tray 1A and tray 2D use stock_location_tray_type_small_8x
        tray_type = self.env.ref(
            "stock_location_tray.stock_location_tray_type_small_8x"
        )

        tray_type.write({"location_storage_type_ids": [(6, 0, self.storage_types.ids)]})

        self.assertEqual(self.location_1a.location_storage_type_ids, self.storage_types)
        self.assertEqual(self.location_2d.location_storage_type_ids, self.storage_types)

    def test_location_create_sync(self):
        # both tray 1A and tray 2D use stock_location_tray_type_small_8x
        tray_type = self.env.ref(
            "stock_location_tray.stock_location_tray_type_small_8x"
        )
        tray_type.write({"location_storage_type_ids": [(6, 0, self.storage_types.ids)]})

        locations = self.location_2a | self.location_2b

        self.assertNotEqual(
            self.location_2a.location_storage_type_ids, self.storage_types
        )
        self.assertNotEqual(
            self.location_2b.location_storage_type_ids, self.storage_types
        )

        locations.tray_type_id = tray_type

        self.assertEqual(self.location_2a.location_storage_type_ids, self.storage_types)
        self.assertEqual(self.location_2b.location_storage_type_ids, self.storage_types)
