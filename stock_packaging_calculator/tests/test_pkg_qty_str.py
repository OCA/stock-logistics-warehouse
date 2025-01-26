# Copyright 2021 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from .common import TestCommon


class TestAsStr(TestCommon):
    def test_as_str(self):
        self.assertEqual(self.product_a.product_qty_by_packaging_as_str(10), "10 Units")
        self.assertEqual(
            self.product_a.product_qty_by_packaging_as_str(10, only_packaging=True), ""
        )
        self.assertEqual(self.product_a.product_qty_by_packaging_as_str(100), "2 Box")
        self.assertEqual(
            self.product_a.product_qty_by_packaging_as_str(250), "1 Big Box,\xa01 Box"
        )
        self.assertEqual(
            self.product_a.product_qty_by_packaging_as_str(255),
            "1 Big Box,\xa01 Box,\xa05 Units",
        )
        # only_packaging has no impact if we get not only units
        self.assertEqual(
            self.product_a.product_qty_by_packaging_as_str(255, only_packaging=True),
            "1 Big Box,\xa01 Box,\xa05 Units",
        )

    def test_as_str_w_units(self):
        self.assertEqual(
            self.product_a.product_qty_by_packaging_as_str(
                10, include_total_units=True
            ),
            "10 Units",
        )
        self.assertEqual(
            self.product_a.product_qty_by_packaging_as_str(
                100, include_total_units=True
            ),
            "2 Box (100 Units)",
        )
        self.assertEqual(
            self.product_a.product_qty_by_packaging_as_str(
                250, include_total_units=True
            ),
            "1 Big Box,\xa01 Box (250 Units)",
        )
        self.assertEqual(
            self.product_a.product_qty_by_packaging_as_str(
                255, include_total_units=True
            ),
            "1 Big Box,\xa01 Box,\xa05 Units (255 Units)",
        )
        # only_packaging has no impact if we get not only units
        self.assertEqual(
            self.product_a.product_qty_by_packaging_as_str(
                255, include_total_units=True, only_packaging=True
            ),
            "1 Big Box,\xa01 Box,\xa05 Units (255 Units)",
        )

    def test_as_str_custom_name(self):
        self.assertEqual(
            self.product_a.with_context(
                _qty_by_packaging_as_str=lambda pkg, qty: f"{pkg.name} {qty} FOO"
            ).product_qty_by_packaging_as_str(250),
            "Big Box 1 FOO,\xa0Box 1 FOO",
        )
