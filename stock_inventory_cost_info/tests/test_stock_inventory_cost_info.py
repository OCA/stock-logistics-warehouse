# Copyright 2019 Tecnativa - Ernesto Tejeda
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockInventoryCostInfo(TransactionCase):
    def setUp(self):
        super().setUp()
        product_obj = self.env["product.product"]
        self.product_1 = product_obj.create(
            {"name": "product test 1", "type": "product", "standard_price": 1000}
        )
        self.product_2 = product_obj.create(
            {"name": "product test 2", "type": "product", "standard_price": 2000}
        )
        self.inventory = self.env["stock.inventory"].create(
            {
                "name": "Another inventory",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "product_qty": 10,
                            "location_id": self.env.ref(
                                "stock.warehouse0"
                            ).lot_stock_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_2.id,
                            "product_qty": 20,
                            "location_id": self.env.ref(
                                "stock.warehouse0"
                            ).lot_stock_id.id,
                        },
                    ),
                ],
            }
        )

    def test_compute_adjustment_cost(self):
        """Tests if the adjustment_cost is correctly computed."""
        lines = self.inventory.line_ids
        line1 = lines.filtered(lambda r: r.product_id == self.product_1)
        self.assertEqual(line1.adjustment_cost, 10000)
        line2 = lines.filtered(lambda r: r.product_id == self.product_2)
        self.assertEqual(line2.adjustment_cost, 40000)
