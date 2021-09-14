# Copyright 2021 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from odoo.addons.stock_packaging_calculator.tests.common import TestCommon
from odoo.addons.stock_packaging_calculator.tests.utils import make_pkg_values


class TestCalc(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.type_retail_box = cls.env["product.packaging.type"].create(
            {"name": "Retail Box", "code": "PACK", "sequence": 3}
        )
        cls.type_transport_box = cls.env["product.packaging.type"].create(
            {"name": "Transport Box", "code": "CASE", "sequence": 4}
        )
        cls.type_pallet = cls.env["product.packaging.type"].create(
            {"name": "Pallet", "code": "PALLET", "sequence": 5}
        )
        cls.pkg_box.packaging_type_id = cls.type_retail_box
        cls.pkg_big_box.packaging_type_id = cls.type_transport_box
        cls.pkg_pallet.packaging_type_id = cls.type_pallet

    def test_calc_1(self):
        expected = [
            make_pkg_values(self.pkg_pallet, qty=1, name=self.type_pallet.name),
            make_pkg_values(self.pkg_big_box, qty=3, name=self.type_transport_box.name),
            make_pkg_values(self.pkg_box, qty=1, name=self.type_retail_box.name),
            make_pkg_values(self.uom_unit, qty=5),
        ]
        self.assertEqual(self.product_a.product_qty_by_packaging(2655), expected)

    def test_calc_2(self):
        expected = [
            make_pkg_values(self.pkg_big_box, qty=1, name=self.type_transport_box.name),
            make_pkg_values(self.pkg_box, qty=3, name=self.type_retail_box.name),
        ]
        self.assertEqual(self.product_a.product_qty_by_packaging(350), expected)

    def test_as_str(self):
        self.assertEqual(self.product_a.product_qty_by_packaging_as_str(10), "10 Units")
        self.assertEqual(self.product_a.product_qty_by_packaging_as_str(100), "2PACK")
        self.assertEqual(
            self.product_a.product_qty_by_packaging_as_str(250), "1CASE,\xa01PACK"
        )
        self.assertEqual(
            self.product_a.with_context(
                qty_by_packaging_type_fname="name",
                qty_by_packaging_type_compact=False,
            ).product_qty_by_packaging_as_str(250),
            "1 Transport Box,\xa01 Retail Box",
        )
