# Copyright 2017-2024 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import new_test_user, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestInventoryDiscrepancy(BaseCommon):
    _test_user_groups = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.inventory_discrepancy_enable = True
        cls.obj_location = cls.env["stock.location"]
        cls.obj_product = cls.env["product.product"]
        cls.obj_warehouse = cls.env["stock.warehouse"]
        cls.obj_quant = cls.env["stock.quant"].with_context(inventory_mode=False)

        cls.product1 = cls.obj_product.create(
            {
                "name": "Test Product 1",
                "type": "consu",
                "is_storable": True,
                "default_code": "PROD1",
            }
        )
        cls.product2 = cls.obj_product.create(
            {
                "name": "Test Product 2",
                "type": "consu",
                "is_storable": True,
                "default_code": "PROD2",
            }
        )
        cls.test_loc = cls.obj_location.create(
            {"name": "Test Location", "usage": "internal", "discrepancy_threshold": 10}
        )
        cls.test_wh = cls.obj_warehouse.create(
            {"name": "Test WH", "code": "T", "discrepancy_threshold": 20}
        )
        cls.obj_location._parent_store_compute()

        # Create Stock manager able to force validation on inventories.
        cls.manager = new_test_user(
            cls.env,
            "manager",
            groups="stock.group_stock_manager"
            ",stock_inventory_discrepancy.group_stock_inventory_validation_always",
        )
        cls.user = new_test_user(
            cls.env,
            "user",
            groups="stock.group_stock_user"
            ",stock_inventory_discrepancy.group_stock_inventory_validation",
        )

        cls.user_2 = new_test_user(
            cls.env,
            "user_2",
            groups="stock.group_stock_user"
            ",stock_inventory_discrepancy.group_stock_inventory_validation_always",
        )
        cls.no_user = new_test_user(
            cls.env,
            "no_user",
            groups="base.group_user",
        )
        cls.quant_line1 = cls.obj_quant.create(
            {
                "product_id": cls.product1.id,
                "quantity": 2.0,
                "location_id": cls.test_loc.id,
            }
        )
        cls.quant_line2 = cls.obj_quant.create(
            {
                "product_id": cls.product2.id,
                "quantity": 4.0,
                "location_id": cls.test_loc.id,
            }
        )

    def test_discrepancy_validation(self):
        """Tests the new workflow"""
        # quant_line1 is over discrepancy but quant_line2 is not
        self.quant_line1.write(
            {
                "inventory_quantity": 3.0,
                "inventory_quantity_set": True,
            }
        )
        self.quant_line1._compute_discrepancy_threshold()
        self.assertEqual(self.quant_line1.discrepancy_threshold, 10)
        self.assertEqual(self.quant_line1.discrepancy_percent, 50)
        self.assertTrue(self.quant_line1.has_over_discrepancy)
        self.quant_line2.inventory_quantity = 4.1
        self.quant_line2._compute_discrepancy_threshold()
        self.assertEqual(self.quant_line1.discrepancy_threshold, 10)
        self.assertEqual(self.quant_line2.discrepancy_percent, 2.5)
        self.assertFalse(self.quant_line2.has_over_discrepancy)
        # Select all quants and try to apply the quantity adjustment
        all_quants = self.quant_line1 | self.quant_line2
        action_dic = all_quants.with_user(self.user).action_apply_inventory()
        model_wiz = action_dic["res_model"]
        wiz = (
            self.env[model_wiz]
            .with_user(self.user)
            .with_context(
                action_dic["context"],
                active_model="stock.quant",
                active_ids=all_quants.ids,
            )
            .create({})
        )
        # Apply the wizard with a stock user will get an error
        self.assertEqual(wiz.discrepancy_quant_ids, self.quant_line1)
        with self.assertRaises(UserError):
            wiz.button_apply()
        # Apply the wizard with a stock manager will apply the adjustment
        wiz.with_user(self.manager).button_apply()
        self.assertEqual(self.quant_line1.quantity, 3)
        self.assertEqual(self.quant_line2.quantity, 4.1)

    def test_discrepancy_validation_always(self):
        """Tests the new workflow"""
        self.quant_line1.inventory_quantity = 3.0
        self.quant_line1._compute_discrepancy_threshold()
        self.assertEqual(self.quant_line1.discrepancy_threshold, 10)
        self.assertEqual(self.quant_line1.discrepancy_percent, 50)
        self.assertTrue(self.quant_line1.has_over_discrepancy)
        self.quant_line2.inventory_quantity = 4.1
        self.quant_line2._compute_discrepancy_threshold()
        self.assertEqual(self.quant_line1.discrepancy_threshold, 10)
        self.assertEqual(self.quant_line2.discrepancy_percent, 2.5)
        self.assertFalse(self.quant_line2.has_over_discrepancy)
        # Select all quants and try to apply the quantity adjustment
        all_quants = self.quant_line1 | self.quant_line2
        action_dic = all_quants.with_user(self.user).action_apply_inventory()
        model_wiz = action_dic["res_model"]
        wiz = (
            self.env[model_wiz]
            .with_user(self.user)
            .with_context(
                action_dic["context"],
                active_model="stock.quant",
                active_ids=all_quants.ids,
            )
            .create({})
        )
        # Apply the wizard with a stock user will get an error
        self.assertEqual(wiz.discrepancy_quant_ids, self.quant_line1)
        with self.assertRaises(UserError):
            wiz.button_apply()
        # Apply the wizard with a stock manager will apply the adjustment
        wiz.with_user(self.user_2).button_apply()
        self.assertEqual(self.quant_line1.quantity, 3)
        self.assertEqual(self.quant_line2.quantity, 4.1)

    def test_warehouse_threshold(self):
        """Tests the behaviour if the threshold is set on the WH."""
        quant_other_loc = self.obj_quant.create(
            {
                "product_id": self.product1.id,
                "inventory_quantity": 3.0,
                "location_id": self.test_wh.lot_stock_id.id,
            }
        )
        self.assertEqual(quant_other_loc.discrepancy_threshold, 20)

    def test_propagate_discrepancy_threshold(self):
        view_test_loc = self.obj_location.create(
            {"name": "Test Location", "usage": "view", "discrepancy_threshold": 0.1}
        )
        child_test_loc = self.obj_location.create(
            {
                "name": "Child Test Location",
                "usage": "internal",
                "discrepancy_threshold": 0.2,
                "location_id": view_test_loc.id,
            }
        )
        view_test_loc.write(
            {"discrepancy_threshold": 0.3, "propagate_discrepancy_threshold": True}
        )
        self.assertEqual(
            child_test_loc.discrepancy_threshold,
            0.3,
            "Threshold Discrepancy wrongly propagated",
        )

    def test_discrepancy_without_count_or_stock(self):
        self.quant_line1.inventory_quantity_set = False
        self.assertEqual(self.quant_line1.discrepancy_percent, 0)
        empty_quant = self.obj_quant.create(
            {
                "product_id": self.product1.id,
                "location_id": self.test_wh.lot_stock_id.id,
            }
        )
        empty_quant.inventory_quantity = 2
        self.assertEqual(empty_quant.discrepancy_percent, 0)

    def test_no_discrepancy_threshold(self):
        self.test_loc.discrepancy_threshold = 0
        self.quant_line1.inventory_quantity = self.quant_line1.quantity
        self.assertFalse(self.quant_line1.discrepancy_threshold)
        self.assertFalse(self.quant_line1.has_over_discrepancy)

    def test_search_over_discrepancy(self):
        self.quant_line1.inventory_quantity = 3
        self.quant_line2.inventory_quantity = 4
        candidates = self.quant_line1 | self.quant_line2
        for operator, value, expected in (
            ("=", True, self.quant_line1),
            ("=", False, self.quant_line2),
            ("!=", True, self.quant_line2),
            ("!=", False, self.quant_line1),
        ):
            with self.subTest(operator=operator, value=value):
                found = self.obj_quant.search(
                    [
                        ("id", "in", candidates.ids),
                        ("has_over_discrepancy", operator, value),
                    ]
                )
                self.assertEqual(found, expected)
        for value, expected in (
            ("True", self.quant_line1),
            ("False", self.quant_line2),
        ):
            domain = self.obj_quant._search_has_over_discrepancy("=", value)
            self.assertEqual(
                self.obj_quant.search([("id", "in", candidates.ids)] + domain), expected
            )
        with self.assertRaisesRegex(UserError, "operator is not supported"):
            self.obj_quant._search_has_over_discrepancy(">", True)
        with self.assertRaisesRegex(UserError, "Value should be True or False"):
            self.obj_quant._search_has_over_discrepancy("=", "invalid")

    def test_apply_under_threshold(self):
        self.quant_line1.inventory_quantity = 2.1
        self.quant_line1.with_user(self.user).action_apply_inventory()
        self.assertEqual(self.quant_line1.quantity, 2.1)

    def test_discrepancy_control_disabled(self):
        self.env.company.inventory_discrepancy_enable = False
        self.quant_line1.inventory_quantity = 3
        self.assertTrue(self.quant_line1.has_over_discrepancy)
        self.quant_line1.with_user(self.user).action_apply_inventory()
        self.assertEqual(self.quant_line1.quantity, 3)

    def test_apply_inventory_requires_validation_group(self):
        stock_user = new_test_user(
            self.env, "stock_user_without_validation", groups="stock.group_stock_user"
        )
        self.quant_line1.inventory_quantity = 2.1
        with self.assertRaisesRegex(UserError, "Only a stock manager can validate"):
            self.quant_line1.with_user(stock_user)._apply_inventory()
        self.assertEqual(self.quant_line1.quantity, 2)

    def test_wizard_without_selected_quants(self):
        wizard = (
            self.env["confirm.discrepancy.wiz"]
            .with_context(discrepancy_quant_ids=[])
            .create({})
        )
        self.assertFalse(wizard.discrepancy_quant_ids)

    def test_recursive_threshold_propagation(self):
        child = self.obj_location.create(
            {"name": "Threshold child", "location_id": self.test_loc.id}
        )
        grandchild = self.obj_location.create(
            {"name": "Threshold grandchild", "location_id": child.id}
        )
        self.test_loc.write(
            {"discrepancy_threshold": 15, "propagate_discrepancy_threshold": True}
        )
        self.assertEqual(child.discrepancy_threshold, 15)
        self.assertEqual(grandchild.discrepancy_threshold, 15)
        self.assertTrue(child.propagate_discrepancy_threshold)
        self.assertTrue(grandchild.propagate_discrepancy_threshold)
