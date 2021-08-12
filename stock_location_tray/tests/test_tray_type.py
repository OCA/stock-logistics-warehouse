# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions

from .common import LocationTrayTypeCase


class TestLocationTrayType(LocationTrayTypeCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.used_tray_type = cls.env.ref(
            "stock_location_tray.stock_location_tray_type_large_16x"
        )
        cls.unused_tray_type = cls.env.ref(
            "stock_location_tray.stock_location_tray_type_small_16x_3"
        )

    def test_tray_type(self):
        # any location created directly under the view is a shuttle
        tray_type = self.env["stock.location.tray.type"].create(
            {"name": "Test Type", "code": "🐵", "rows": 4, "cols": 6}
        )
        self.assertEqual(
            tray_type.tray_matrix,
            {
                "selected": [],  # no selection as this is the "model"
                # a "full" matrix is generated for display on the UI
                # fmt: off
                'cells': [
                    [1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1],
                ]
                # fmt: on
            },
        )
        self.assertEqual(len(tray_type.name_search()), 11)
        self.assertEqual(len(tray_type.name_search("Test")), 1)
        self.assertEqual(len(tray_type.name_search("None")), 0)
        action = tray_type.open_locations()
        self.assertEqual(action["res_model"], "stock.location")
        self.assertEqual(action["domain"], [("tray_type_id", "in", tray_type.ids)])
        self.assertEqual(action["context"], {"default_tray_type_id": tray_type.id})

    def test_check_active(self):
        location = self.tray_location
        location.tray_type_id = self.used_tray_type
        location = self.used_tray_type.location_ids
        self.assertTrue(location)
        message = "cannot be archived.\n\n.*{}*".format(location.name)
        # we cannot archive used ones
        with self.assertRaisesRegex(exceptions.ValidationError, message):
            self.used_tray_type.active = False
        # we can archive unused ones
        self.unused_tray_type.active = False
        # this is to increase test coverage
        self.tray_location.tray_type_id = False

    def test_check_cols_rows(self):
        location = self.tray_location
        location.tray_type_id = self.used_tray_type
        location = self.used_tray_type.location_ids
        self.assertTrue(location)
        message = "size cannot be changed.\n\n.*{}*".format(location.name)
        # we cannot modify size of used ones
        with self.assertRaisesRegex(exceptions.ValidationError, message):
            self.used_tray_type.rows = 10
        with self.assertRaisesRegex(exceptions.ValidationError, message):
            self.used_tray_type.cols = 10
        # we can modify size of unused ones
        self.unused_tray_type.rows = 10
        self.unused_tray_type.cols = 10

    def test_width_per_cell(self):
        tray_type = self.used_tray_type
        tray_type.cols = 10
        tray_type.width = 120
        self.assertEqual(tray_type.width_per_cell, 12)
        tray_type.width = 0
        self.assertEqual(tray_type.width_per_cell, 0)

    def test_depth_per_cell(self):
        tray_type = self.used_tray_type
        tray_type.rows = 10
        tray_type.depth = 120
        self.assertEqual(tray_type.depth_per_cell, 12)
        tray_type.depth = 0
        self.assertEqual(tray_type.depth_per_cell, 0)
