# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions

from .common import TrayTypeCommonCase


class TestTrayTypeLocation(TrayTypeCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tray_type = cls.env.ref(
            "stock_location_tray.stock_location_tray_type_small_8x"
        )
        cls.tray_type.write(
            {"location_storage_type_ids": [(6, 0, cls.storage_types.ids)]}
        )
        cls.locations = cls.location_2a | cls.location_2b

    def test_location_create_sync(self):
        locations = self.env["stock.location"].create(
            [
                {
                    "name": "tray test 1",
                    "location_id": self.shuttle.location_id.id,
                    "usage": "internal",
                    "tray_type_id": self.tray_type.id,
                },
                {
                    "name": "tray test 2",
                    "location_id": self.shuttle.location_id.id,
                    "usage": "internal",
                    "tray_type_id": self.tray_type.id,
                },
            ]
        )
        self.assertEqual(locations[0].location_storage_type_ids, self.storage_types)
        self.assertEqual(locations[1].location_storage_type_ids, self.storage_types)

    def test_location_write_sync(self):
        self.locations.tray_type_id = self.tray_type
        self.assertEqual(self.location_2a.location_storage_type_ids, self.storage_types)
        self.assertEqual(self.location_2b.location_storage_type_ids, self.storage_types)

    def test_location_create_error(self):
        with self.assertRaisesRegex(exceptions.UserError, "Error creating.*"):
            self.env["stock.location"].create(
                [
                    {
                        "name": "tray test 1",
                        "location_id": self.shuttle.location_id.id,
                        "usage": "internal",
                        "tray_type_id": self.tray_type.id,
                        "location_storage_type_ids": [
                            (6, 0, self.location_storage_type_buffer.ids)
                        ],
                    },
                    {
                        "name": "tray test 2",
                        "location_id": self.shuttle.location_id.id,
                        "usage": "internal",
                        "tray_type_id": self.tray_type.id,
                        "location_storage_type_ids": [
                            (6, 0, self.location_storage_type_buffer.ids)
                        ],
                    },
                ]
            )

    def test_location_write_both_fields_error(self):
        with self.assertRaisesRegex(exceptions.UserError, "Error updating.*"):
            self.locations.write(
                {
                    "tray_type_id": self.tray_type.id,
                    "location_storage_type_ids": [
                        (6, 0, self.location_storage_type_buffer.ids)
                    ],
                }
            )

    def test_location_write_storage_type_error(self):
        with self.assertRaisesRegex(exceptions.UserError, "Error updating.*"):
            self.locations.write(
                {
                    "location_storage_type_ids": [
                        (6, 0, self.location_storage_type_buffer.ids)
                    ],
                }
            )
