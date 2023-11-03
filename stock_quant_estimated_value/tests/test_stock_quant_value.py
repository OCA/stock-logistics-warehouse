# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockQuantValue(TransactionCase):
    def setUp(self):
        super().setUp()
        product_obj = self.env["product.product"]
        self.product_1 = product_obj.create(
            {"name": "product test 1", "type": "product", "standard_price": 1000}
        )
        self.product_2 = product_obj.create(
            {"name": "product test 2", "type": "product", "standard_price": 2000}
        )

    def test_compute_value(self):
        """Tests if the adjustment_cost is correctly computed."""
        quant_prod_1 = self.env["stock.quant"].create(
            {
                "product_id": self.product_1.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "quantity": 10.0,
            }
        )
        self.assertEqual(quant_prod_1.estimated_value, 10000)
        quant_prod_2 = self.env["stock.quant"].create(
            {
                "product_id": self.product_2.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "quantity": 20.0,
            }
        )
        self.assertEqual(quant_prod_2.estimated_value, 40000)
