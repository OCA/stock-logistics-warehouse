# Copyright 2019 Tecnativa - Ernesto Tejeda
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockQuantCostInfo(TransactionCase):
    def setUp(self):
        super().setUp()
        product_obj = self.env["product.product"]
        self.product_1 = product_obj.create(
            {"name": "product test 1", "type": "product", "standard_price": 1000}
        )
        self.product_2 = product_obj.create(
            {"name": "product test 2", "type": "product", "standard_price": 2000}
        )

    def test_compute_adjustment_cost(self):
        """Tests if the adjustment_cost is correctly computed."""
        quant_prod_1 = self.env["stock.quant"].create(
            {
                "product_id": self.product_1.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "inventory_quantity": 10.0,
            }
        )
        self.assertEqual(quant_prod_1.adjustment_cost, 10000)
        quant_prod_2 = self.env["stock.quant"].create(
            {
                "product_id": self.product_2.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "inventory_quantity": 20.0,
            }
        )
        self.assertEqual(quant_prod_2.adjustment_cost, 40000)
