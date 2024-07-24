# Copyright 2024 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestStockPackageTypeVolume(TransactionCase):
    def setUp(self):
        super(TestStockPackageTypeVolume, self).setUp()
        self.package_type = self.env["stock.package.type"].new()

    def test_01(self):
        # By default length is in mm and volume in cubic meter
        self.package_type.packaging_length = 1000.0
        self.package_type.height = 1000.0
        self.package_type.width = 1000.0
        self.assertEqual(1.0, self.package_type.volume)
