# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions

from .common import KardexCase


class TestKardexTrayType(KardexCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.used_tray_type = cls.env.ref(
            'stock_kardex.kardex_tray_type_large_16x'
        )
        cls.unused_tray_type = cls.env.ref(
            'stock_kardex.kardex_tray_type_small_16x_3'
        )

    def test_kardex_tray_type(self):
        # any location created directly under the view is a shuttle
        tray_type = self.env['stock.kardex.tray.type'].create(
            {
                'name': 'Test Type',
                'code': '🐵',
                'usage': 'internal',
                'rows': 4,
                'cols': 6,
            }
        )
        self.assertEqual(
            tray_type.tray_matrix,
            {
                'selected': [],  # no selection as this is the "model"
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

    def test_kardex_check_active(self):
        # this type used by tray T1B, we should not be able to disable it
        location = self.used_tray_type.location_ids
        self.assertTrue(location)
        message = 'cannot be archived.*{}.*'.format(location.name)
        # we cannot archive used ones
        with self.assertRaisesRegex(exceptions.ValidationError, message):
            self.used_tray_type.active = False
        # we can archive unused ones
        self.unused_tray_type.active = False

    def test_kardex_check_cols_rows(self):
        # this type used by tray T1B, we should not be able to modify size
        location = self.used_tray_type.location_ids
        self.assertTrue(location)
        message = 'size cannot be changed.*{}.*'.format(location.name)
        # we cannot modify size of used ones
        with self.assertRaisesRegex(exceptions.ValidationError, message):
            self.used_tray_type.rows = 10
        with self.assertRaisesRegex(exceptions.ValidationError, message):
            self.used_tray_type.cols = 10
        # we can modify size of unused ones
        self.unused_tray_type.rows = 10
        self.unused_tray_type.cols = 10
