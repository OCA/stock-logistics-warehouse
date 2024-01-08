# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.tests.common2 import TestStockCommon


class TestStockInventoryJustification(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # MODELS
        cls.stock_inventory_justification_model = cls.env[
            "stock.inventory.justification"
        ]
        cls.stock_quant_model = cls.env["stock.quant"].with_context(inventory_mode=True)
        # INSTANCES
        # Inventory justifications
        cls.inventory_justification_01 = cls.stock_inventory_justification_model.create(
            {"name": "Justification 01"}
        )
        cls.inventory_justification_02 = cls.stock_inventory_justification_model.create(
            {"name": "Justification 02"}
        )
        # Products
        cls.product_1.type = "product"

    def test_01(self):
        """
        Test case:
            - Process a stock inventory on a quant without justification
        Expected result:
            - The created move has no inventory justification
        """
        inventory_quant = self.stock_quant_model.create(
            {
                "product_id": self.product_1.id,
                "inventory_quantity": 50.0,
                "location_id": self.warehouse_1.lot_stock_id.id,
            }
        )
        inventory_quant.action_apply_inventory()
        stock_move = self.env["stock.move"].search(
            [("is_inventory", "=", True), ("product_id", "=", self.product_1.id)]
        )
        self.assertFalse(stock_move.inventory_justification_ids)

    def test_02(self):
        """
        Test case:
            - Process a stock inventory on a quant with justification
        Expected result:
            - The created move has the same inventory justification as the quant
        """
        inventory_quant = self.stock_quant_model.create(
            {
                "product_id": self.product_1.id,
                "inventory_quantity": 50.0,
                "location_id": self.warehouse_1.lot_stock_id.id,
                "inventory_justification_ids": [
                    (6, 0, [self.inventory_justification_01.id])
                ],
            }
        )
        inventory_quant.action_apply_inventory()
        stock_move = self.env["stock.move"].search(
            [("is_inventory", "=", True), ("product_id", "=", self.product_1.id)]
        )
        self.assertFalse(inventory_quant.inventory_justification_ids)
        self.assertEqual(
            stock_move.inventory_justification_ids, self.inventory_justification_01
        )
