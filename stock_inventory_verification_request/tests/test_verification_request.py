# Copyright 2020 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.exceptions import AccessError


class TestStockVerificationRequest(common.TransactionCase):
    def setUp(self):
        super().setUp()
        # disable tracking test suite wise
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.user_model = self.env["res.users"].with_context(no_reset_password=True)

        self.obj_wh = self.env["stock.warehouse"]
        self.obj_location = self.env["stock.location"]
        self.obj_inventory = self.env["stock.inventory"]
        self.obj_product = self.env["product.product"]
        self.obj_svr = self.env["stock.slot.verification.request"]
        self.obj_move = self.env["stock.move"]
        self.stock_quant_obj = self.env["stock.quant"]

        self.product1 = self.obj_product.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "default_code": "PROD1",
            }
        )
        self.product2 = self.obj_product.create(
            {
                "name": "Test Product 2",
                "type": "product",
                "default_code": "PROD2",
            }
        )
        self.test_loc = self.obj_location.create(
            {"name": "Test Location", "usage": "internal", "discrepancy_threshold": 0.1}
        )

        # Create Stock manager able to force validation on inventories.
        group_stock_man = self.env.ref("stock.group_stock_manager")
        group_inventory_all = self.env.ref(
            "stock_inventory_discrepancy." "group_stock_inventory_validation_always"
        )
        self.manager = self.env["res.users"].create(
            {
                "name": "Test Manager",
                "login": "manager",
                "email": "test.manager@example.com",
                "groups_id": [(6, 0, [group_stock_man.id, group_inventory_all.id])],
            }
        )
        group_stock_user = self.env.ref("stock.group_stock_user")
        self.user = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "user",
                "email": "test.user@example.com",
                "groups_id": [(6, 0, [group_stock_user.id])],
            }
        )
        self.quant1 = self.stock_quant_obj.create(
            {
                "location_id": self.test_loc.id,
                "product_id": self.product1.id,
                "inventory_quantity": 20.0,
            }
        ).action_apply_inventory()
        self.quant2 = self.stock_quant_obj.create(
            {
                "location_id": self.test_loc.id,
                "product_id": self.product2.id,
                "inventory_quantity": 30.0,
            }
        ).action_apply_inventory()

    def test_svr_creation(self):
        """Tests the creation of Slot Verification Requests."""
        inventory = self.obj_inventory.create(
            {
                "name": "Generate over discrepancy in both lines.",
                "product_selection": "manual",
                "location_ids": [(6, 0, [self.test_loc.id])],
                "product_ids": [(6, 0, [self.product1.id, self.product2.id])],
            }
        )
        inventory.action_state_to_in_progress()
        self.assertEqual(
            inventory.state,
            "in_progress",
            "Inventory Adjustment not changing to Pending to " "Approve.",
        )
        previous_count = len(self.obj_svr.search([]))
        for quant in inventory.stock_quant_ids:
            quant.write({"inventory_quantity": 10.0})
            quant.action_request_verification()
        current_count = len(self.obj_svr.search([]))
        self.assertEqual(
            current_count, previous_count + 2, "Slot Verification Request not created."
        )
        # Test the method to open SVR from quants
        for quant in inventory.stock_quant_ids:
            quant.action_open_svr()

    def test_svr_workflow(self):
        """Tests workflow of Slot Verification Request."""
        test_svr = self.env["stock.slot.verification.request"].create(
            {
                "location_id": self.test_loc.id,
                "state": "wait",
                "product_id": self.product1.id,
            }
        )
        self.assertEqual(
            test_svr.state,
            "wait",
            "Slot Verification Request not created from scratch.",
        )
        with self.assertRaises(AccessError):
            test_svr.with_user(self.user).action_confirm()
        test_svr.action_confirm()
        self.assertEqual(
            test_svr.state, "open", "Slot Verification Request not confirmed properly."
        )
        test_svr.action_solved()
        self.assertEqual(
            test_svr.state, "done", "Slot Verification Request not marked as solved."
        )
        test_svr.action_cancel()
        self.assertEqual(
            test_svr.state,
            "cancelled",
            "Slot Verification Request not marked as cancelled.",
        )

    def test_view_methods(self):
        """Tests the methods used to handle de UI."""
        test_svr = self.env["stock.slot.verification.request"].create(
            {
                "location_id": self.test_loc.id,
                "state": "wait",
                "product_id": self.product1.id,
            }
        )
        test_svr.action_confirm()
        self.assertEqual(test_svr.involved_quant_count, 1, "Unexpected involved move")
        self.assertEqual(
            test_svr.involved_quant_count, 1, "Unexpected involved inventory line"
        )
        test_svr.action_view_move_lines()
        test_svr.action_view_quants()

    def test_svr_full_workflow(self):
        test_svr = self.env["stock.slot.verification.request"].create(
            {
                "location_id": self.test_loc.id,
                "state": "wait",
                "product_id": self.product1.id,
            }
        )
        self.assertEqual(
            test_svr.state,
            "wait",
            "Slot Verification Request not created in waiting state.",
        )
        test_svr.action_confirm()
        self.assertEqual(
            test_svr.state, "open", "Slot Verification Request not confirmed properly."
        )
        test_svr.action_solved()
        self.assertEqual(
            test_svr.state, "done", "Slot Verification Request not marked as solved."
        )
        test_svr.write({"state": "wait"})
        test_svr.action_confirm()
        test_svr.action_cancel()
        self.assertEqual(
            test_svr.state,
            "cancelled",
            "Slot Verification Request not marked as cancelled.",
        )

    def test_user_permissions_on_svr(self):
        """Tests that users without the correct permissions cannot change SVR state."""
        test_svr = self.env["stock.slot.verification.request"].create(
            {
                "location_id": self.test_loc.id,
                "state": "wait",
                "product_id": self.product1.id,
            }
        )
        with self.assertRaises(AccessError):
            test_svr.with_user(self.user).action_confirm()
        test_svr.action_confirm()
        with self.assertRaises(AccessError):
            test_svr.with_user(self.user).action_solved()


def test_action_view_methods(self):
    """Tests the view methods in Slot Verification Request."""
    svr = self.obj_svr.create(
        {
            "location_id": self.test_loc.id,
            "state": "wait",
            "product_id": self.product1.id,
        }
    )
    svr.action_view_move_lines()
    svr.action_view_quants()
    svr.action_create_inventory_adjustment()
    svr.action_view_inventories()
