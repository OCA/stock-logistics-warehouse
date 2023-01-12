# pylint: disable=import-error,protected-access,too-few-public-methods
# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2019-2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockQuantityChangeReason(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockQuantityChangeReason, cls).setUpClass()

        # MODELS
        cls.stock_move_line = cls.env["stock.move.line"]
        cls.product_product_model = cls.env["product.product"]
        cls.product_category_model = cls.env["product.category"]
        cls.stock_quant = cls.env["stock.quant"]
        cls.preset_reason_id = cls.env["stock.quant.reason"]
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        # INSTANCES
        cls.category = cls.product_category_model.create({"name": "Physical (test)"})

    def _create_product(self, name):
        return self.product_product_model.create(
            {"name": name, "categ_id": self.category.id, "type": "product"}
        )

    def _product_change_qty(self, product, location, new_qty):
        values = {
            "product_id": product.id,
            "location_id": location.id,
            "inventory_quantity": new_qty,
        }
        self.stock_quant.with_context(inventory_mode=True).create(values)

    def _create_reason(self, name, description=None):
        return self.preset_reason_id.create({"name": name, "description": description})

    def test_inventory_adjustment_onchange_reason_preset_reason(self):
        """Check that adding a reason or a preset reason explode to lines"""
        product2 = self._create_product("product_product_2")
        self._product_change_qty(product2, self.stock_location, 50)
        inventory_quant = self.env["stock.quant"].create(
            {
                "product_id": product2.id,
                "location_id": self.stock_location.id,
                "inventory_quantity": 10,
            }
        )
        inventory_quant.user_id = self.env.user.id
        inventory_quant.inventory_quantity_set = True
        preset_reason_id = self._create_reason("Test 1", "Description Test 1")
        inventory_quant.preset_reason_id = preset_reason_id
        inventory_quant.action_apply_inventory()
        move_line = self.stock_move_line.search(
            [("product_id", "=", product2.id), ("preset_reason_id", "!=", False)]
        )
        self.assertEqual(len(move_line), 1)
        self.assertEqual(inventory_quant.preset_reason_id.name, False)
        self.assertEqual(move_line.move_id.origin, preset_reason_id.name)
        self.assertEqual(move_line.preset_reason_id, preset_reason_id)
