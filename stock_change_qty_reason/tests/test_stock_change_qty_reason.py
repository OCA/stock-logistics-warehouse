# pylint: disable=import-error,protected-access,too-few-public-methods
# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockQuantityChangeReason(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockQuantityChangeReason, cls).setUpClass()

        # MODELS
        cls.stock_move = cls.env["stock.move"]
        cls.product_product_model = cls.env["product.product"]
        cls.product_category_model = cls.env["product.category"]
        cls.wizard_model = cls.env["stock.change.product.qty"]
        cls.preset_reason_id = cls.env["stock.inventory.line.reason"]
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        # INSTANCES
        cls.category = cls.product_category_model.create({"name": "Physical (test)"})

    def _create_product(self, name):
        return self.product_product_model.create(
            {"name": name, "categ_id": self.category.id, "type": "product"}
        )

    def _product_change_qty(self, product, new_qty):
        values = {
            "product_tmpl_id": product.product_tmpl_id.id,
            "product_id": product.id,
            "new_quantity": new_qty,
        }
        wizard = self.wizard_model.create(values)
        wizard.change_product_qty()

    def _create_reason(self, name, description=None):
        return self.preset_reason_id.create({"name": name, "description": description})

    def test_inventory_adjustment_onchange_reason_preset_reason(self):
        """Check that adding a reason or a preset reason explode to lines"""
        product2 = self._create_product("product_product_2")
        self._product_change_qty(product2, 50)
        inventory = self.env["stock.inventory"].create(
            {
                "name": "remove product2",
                "product_ids": [(4, product2.id)],
                "location_ids": [(4, self.stock_location.id)],
            }
        )
        inventory.preset_reason_id = self._create_reason("Test 1", "Description Test 1")
        inventory.action_start()
        self.assertEqual(len(inventory.line_ids), 1)
        inventory.reason = "Reason 2"
        inventory.onchange_reason()
        self.assertEqual(inventory.line_ids.reason, inventory.reason)
        inventory.preset_reason_id = self._create_reason("Test 2", "Description Test 2")
        inventory.onchange_preset_reason()
        self.assertEqual(
            inventory.line_ids.preset_reason_id, inventory.preset_reason_id
        )
        inventory.line_ids[0].write({"product_qty": 10})
        inventory.action_validate()
        move = self.stock_move.search(
            [("product_id", "=", product2.id), ("preset_reason_id", "!=", False)]
        )
        self.assertEqual(len(move), 1)
        self.assertEqual(move.origin, inventory.preset_reason_id.name)
        self.assertEqual(move.preset_reason_id, inventory.preset_reason_id)
