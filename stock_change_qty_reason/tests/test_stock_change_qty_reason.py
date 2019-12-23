# pylint: disable=import-error,protected-access,too-few-public-methods
# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
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

    def _product_change_qty(self, product, new_qty, reason, preset_reason_id=None):
        values = {"product_id": product.id, "new_quantity": new_qty, "reason": reason}
        if preset_reason_id:
            values.update({"preset_reason_id": preset_reason_id.id})
        wizard = self.wizard_model.create(values)
        wizard.change_product_qty()

    def _create_reason(self, name, description=None):
        return self.preset_reason_id.create({"name": name, "description": description})

    def test_product_change_qty(self):
        """ Check product quantity update move reason is well set
        """

        # create products
        product2 = self._create_product("product_product_2")
        product3 = self._create_product("product_product_3")
        product4 = self._create_product("product_product_4")
        product5 = self._create_product("product_product_5")
        product6 = self._create_product("product_product_6")

        # update qty on hand and add reason
        self._product_change_qty(product2, 10, "product_2_reason")
        self._product_change_qty(product3, 0, "product_3_reason")
        self._product_change_qty(product4, 0, "product_4_reason")
        self._product_change_qty(product5, 10, "product_5_reason")
        self._product_change_qty(product6, 0, "product_6_reason")

        # check stock moves created
        move2 = self.stock_move.search([("product_id", "=", product2.id)])
        move3 = self.stock_move.search([("product_id", "=", product3.id)])
        move4 = self.stock_move.search([("product_id", "=", product4.id)])
        move5 = self.stock_move.search([("product_id", "=", product5.id)])
        move6 = self.stock_move.search([("product_id", "=", product6.id)])

        self.assertEqual(move2.origin, "product_2_reason")
        self.assertFalse(move3)
        self.assertFalse(move4)
        self.assertEqual(move5.origin, "product_5_reason")
        self.assertFalse(move6)

    def test_product_change_qty_with_preset_reason(self):
        """ Check product quantity update move reason is well set
        """
        # create reason
        reason = self._create_reason("Test", "Description Test")
        # create products
        product2 = self._create_product("product_product_2")
        product3 = self._create_product("product_product_3")

        # update qty on hand and add reason
        self._product_change_qty(product2, 10, reason.name, reason)
        self._product_change_qty(product3, 0, reason.name, reason)

        # check stock moves created
        move2 = self.stock_move.search([("product_id", "=", product2.id)])
        move3 = self.stock_move.search([("product_id", "=", product3.id)])
        # asserts
        self.assertEqual(move2.origin, reason.name)
        self.assertEqual(move2.preset_reason_id, reason)
        self.assertFalse(move3)

    def test_inventory_adjustment_onchange_reason_preset_reason(self):
        """ Check that adding a reason or a preset reason explode to lines
        """
        product2 = self._create_product("product_product_2")
        self._product_change_qty(product2, 50, "product_2_reason")
        inventory = self.env["stock.inventory"].create(
            {
                "name": "remove product2",
                "filter": "product",
                "location_id": self.stock_location.id,
                "product_id": product2.id,
            }
        )
        inventory.preset_reason_id = self._create_reason("Test 1", "Description Test 1")
        inventory.action_start()
        self.assertEqual(len(inventory.line_ids), 1)
        inventory.preset_reason_id = self._create_reason("Test 2", "Description Test 2")
        inventory.onchange_preset_reason()
        self.assertEquals(
            inventory.line_ids.preset_reason_id, inventory.preset_reason_id
        )
        inventory.reason = "Reason 2"
        inventory.onchange_reason()
        self.assertEquals(inventory.line_ids.reason, inventory.reason)
