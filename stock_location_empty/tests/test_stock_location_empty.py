# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestStockLocationChildren(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_input = cls.env["stock.location"].create(
            {
                "name": "Test",
                "usage": "internal",
            }
        )
        product_1 = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "type": "consu",
                "is_storable": True,
            }
        )
        product_2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": product_1.id,
                "location_id": cls.stock_input.id,
                "quantity": 60,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": product_2.id,
                "location_id": cls.stock_input.id,
                "quantity": 50,
            }
        )

    def test_stock_location_amount(self):
        self.assertEqual(self.stock_input.stock_amount, 110.0)
        location_record = self.env["stock.location"].search(
            [("stock_amount", "=", 110.0)]
        )
        self.assertEqual(location_record.stock_amount, 110)
        record_search = self.env["stock.location"].search(
            [("stock_amount", "in", [110, 111])]
        )
        self.assertEqual(record_search, self.stock_input)
