# Copyright 2026 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPackagingVolumeCompute(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.packaging = cls.env["stock.package"].new()
        cls.packaging2 = cls.env["stock.package"].new()
        cls.packaging3 = cls.env["stock.package"].new()

        uom_env = cls.env["uom.uom"].with_context(active_test=False)
        cls.uom_m = uom_env.search([("name", "=", "m")])
        cls.uom_cm = uom_env.search([("name", "=", "cm")])
        cls.uom_L = uom_env.search([("name", "=", "L")])
        cls.uom_m3 = uom_env.search([("name", "=", "m³")])
        cls.uom_ft = uom_env.search([("name", "=", "ft")])
        cls.uom_ft3 = uom_env.search([("name", "=", "ft³")])

    def test_input_uom(self):
        # Volume always in m3 (using default parameter), but with different initial UoM.

        # Initial dimensions in meter
        self.packaging.packaging_length = 10.0
        self.packaging.height = 10.0
        self.packaging.width = 10.0
        self.packaging.length_uom_id = self.uom_m
        self.packaging.volume_uom_id = self.uom_m3
        self.packaging._compute_volume()
        self.assertEqual(1000, self.packaging.volume)

        #  Initial dimensions in cm
        self.packaging2.packaging_length = 10.0
        self.packaging2.height = 10.0
        self.packaging2.width = 10.0
        self.packaging2.length_uom_id = self.uom_cm
        self.packaging2.volume_uom_id = self.uom_m3
        self.packaging2._compute_volume()
        self.assertEqual(0.001, self.packaging2.volume)

        # Initial dimensions in feet
        self.packaging3.packaging_length = 10.0
        self.packaging3.height = 10.0
        self.packaging3.width = 10.0
        self.packaging3.length_uom_id = self.uom_ft
        self.packaging3.volume_uom_id = self.uom_m3
        self.packaging3._compute_volume()
        self.assertEqual(28.3168, self.packaging3.volume)

    def test_compute_volume(self):
        # initial UoM always in meters and Volume in m3, but with different dimensions.

        self.packaging.packaging_length = 10
        self.packaging.height = 8
        self.packaging.width = 10
        self.packaging.length_uom_id = self.uom_m
        self.packaging.volume_uom_id = self.uom_m3
        self.packaging._compute_volume()
        self.assertEqual(800, self.packaging.volume)

        self.packaging2.packaging_length = 6.0
        self.packaging2.height = 14.0
        self.packaging2.width = 1.0
        self.packaging2.length_uom_id = self.uom_m
        self.packaging2.volume_uom_id = self.uom_m3
        self.packaging2._compute_volume()
        self.assertEqual(84.0, self.packaging2.volume)

        self.packaging3.packaging_length = 100.0
        self.packaging3.height = 50
        self.packaging3.width = 80
        self.packaging3.length_uom_id = self.uom_m
        self.packaging3.volume_uom_id = self.uom_m3
        self.packaging3._compute_volume()
        self.assertEqual(400000, self.packaging3.volume)

    def test_output_uom(self):
        # Tests with both different initial and volume UoMs.

        # feet to Liters
        self.packaging.packaging_length = 10.0
        self.packaging.height = 10.0
        self.packaging.width = 10.0
        self.packaging.length_uom_id = self.uom_ft
        self.packaging.volume_uom_id = self.uom_L
        self.packaging._compute_volume()
        self.assertAlmostEqual(28316.8439, self.packaging.volume, places=1)

        #  cm to cubic feet
        self.packaging2.packaging_length = 10.0
        self.packaging2.height = 10.0
        self.packaging2.width = 10.0
        self.packaging2.length_uom_id = self.uom_cm
        self.packaging2.volume_uom_id = self.uom_ft3
        self.packaging2._compute_volume()
        self.assertAlmostEqual(0.0353, self.packaging2.volume, places=4)

        # meters to cubic feet
        self.packaging3.packaging_length = 10.0
        self.packaging3.height = 10.0
        self.packaging3.width = 10.0
        self.packaging3.length_uom_id = self.uom_m
        self.packaging3.volume_uom_id = self.uom_ft3
        self.packaging3._compute_volume()
        self.assertAlmostEqual(35314.7248, self.packaging3.volume, places=0)
