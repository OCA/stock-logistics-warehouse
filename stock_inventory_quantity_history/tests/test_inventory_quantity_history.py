# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestInventoryQuantityHistory(TransactionCase):
    def test_inventory_theoretical_quantity(self):
        product = self.env.ref("product.product_product_8")
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "inventory_quantity": 32.0,
            }
        )._apply_inventory()
        history_sml = self.env["stock.move.line"].search(
            [("product_id", "=", product.id), ("is_inventory", "=", True)],
            order="id desc",
            limit=1,
        )
        self.assertEqual(history_sml.inventory_theoretical_qty, 0.0)
        self.assertEqual(history_sml.inventory_real_qty, 32.0)
