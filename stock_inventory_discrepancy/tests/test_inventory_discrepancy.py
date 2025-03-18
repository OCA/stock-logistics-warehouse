# Copyright 2017-2020 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestInventoryDiscrepancy(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env.company.inventory_discrepancy_enable = True
        self.obj_location = self.env["stock.location"]
        self.obj_product = self.env["product.product"]
        self.obj_warehouse = self.env["stock.warehouse"]
        self.obj_quant = self.env["stock.quant"]

        self.product1 = self.obj_product.create(
            {"name": "Test Product 1", "type": "product", "default_code": "PROD1"}
        )
        self.product2 = self.obj_product.create(
            {"name": "Test Product 2", "type": "product", "default_code": "PROD2"}
        )
        self.test_loc = self.obj_location.create(
            {"name": "Test Location", "usage": "internal", "discrepancy_threshold": 10}
        )
        self.test_wh = self.obj_warehouse.create(
            {"name": "Test WH", "code": "T", "discrepancy_threshold": 20}
        )
        self.obj_location._parent_store_compute()

        # Create Stock manager able to force validation on inventories.
        group_stock_man = self.env.ref("stock.group_stock_manager")
        group_inventory_all = self.env.ref(
            "stock_inventory_discrepancy.group_stock_inventory_validation_always"
        )
        group_employee = self.env.ref("base.group_user")

        self.manager = self.env["res.users"].create(
            {
                "name": "Test Manager",
                "login": "manager",
                "email": "test.manager@example.com",
                "groups_id": [(6, 0, [group_stock_man.id, group_inventory_all.id])],
            }
        )
        group_stock_user = self.env.ref("stock.group_stock_user")
        group_inventory = self.env.ref(
            "stock_inventory_discrepancy.group_stock_inventory_validation"
        )
        self.user = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "user",
                "email": "test.user@example.com",
                "groups_id": [(6, 0, [group_stock_user.id, group_inventory.id])],
            }
        )

        self.user_2 = self.env["res.users"].create(
            {
                "name": "Test User 2",
                "login": "user_2",
                "email": "test2.user@example.com",
                "groups_id": [(6, 0, [group_stock_user.id, group_inventory_all.id])],
            }
        )

        self.no_user = self.env["res.users"].create(
            {
                "name": "No User",
                "login": "no_user",
                "email": "test.no_user@example.com",
                "groups_id": [(6, 0, [group_employee.id])],
            }
        )

        self.quant_line1 = self.obj_quant.with_context(inventory_mode=False).create(
            {
                "product_id": self.product1.id,
                "quantity": 2.0,
                "location_id": self.test_loc.id,
            }
        )
        self.quant_line2 = self.obj_quant.with_context(inventory_mode=False).create(
            {
                "product_id": self.product2.id,
                "quantity": 4.0,
                "location_id": self.test_loc.id,
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
        quant_other_loc = self.obj_quant.with_context(inventory_mode=False).create(
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
