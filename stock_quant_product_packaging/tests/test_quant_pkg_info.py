# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.tests.test_quant import StockQuant


class TestStockQuantInfo(StockQuant):
    def setUp(self):
        super().setUp()
        self.pkg_1 = self.env["product.packaging"].create(
            {
                "name": "Packaging",
                "qty": 10.0,
            }
        )
        self.pkg_2 = self.env["product.packaging"].create(
            {
                "name": "Packaging",
                "qty": 25.0,
            }
        )
        self.quant_1 = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.stock_location.id,
                "quantity": 100.0,
            }
        )
        self.pkg_info_1 = self.env["stock.quant.packaging.info"].create(
            {
                "packaging_id": self.pkg_1.id,
                "quant_id": self.quant_1.id,
                "qty": 50.0,
            }
        )
        self.pkg_info_2 = self.env["stock.quant.packaging.info"].create(
            {
                "packaging_id": self.pkg_2.id,
                "quant_id": self.quant_1.id,
                "qty": 50.0,
            }
        )
        self.quant_2 = self.quant_1.copy(
            {"location_id": self.stock_subloc2.id, "quantity": 45.0}
        )
        self.pkg_info_3 = self.env["stock.quant.packaging.info"].create(
            {
                "packaging_id": self.pkg_1.id,
                "quant_id": self.quant_1.id,
                "qty": 20.0,
            }
        )
        self.pkg_info_4 = self.env["stock.quant.packaging.info"].create(
            {
                "packaging_id": self.pkg_2.id,
                "quant_id": self.quant_1.id,
                "qty": 25.0,
            }
        )

    def test_quant_pkg_info(self):
        self.assertEqual(self.pkg_info_1.qty_per_pkg, 10.0)
        self.assertEqual(self.pkg_info_2.qty_per_pkg, 25.0)
        self.assertEqual(self.quant_1.packaging_info_str, "10.0: 50.0, 25.0: 50.0")

    def test_product_pkg_info(self):
        self.assertEqual(
            self.product.stock_quant_packaging_infos,
            "10.0: 50.0, 25.0: 50.0, 10.0: 20.0, 25.0: 25.0",
        )
