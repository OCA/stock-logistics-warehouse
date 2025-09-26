# Copyright 2020 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestStockVerificationRequest(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # disable tracking test suite wise
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)

        cls.obj_wh = cls.env["stock.warehouse"]
        cls.obj_location = cls.env["stock.location"]
        cls.obj_inventory = cls.env["stock.inventory"]
        cls.obj_product = cls.env["product.product"]
        cls.obj_svr = cls.env["stock.slot.verification.request"]
        cls.obj_move = cls.env["stock.move"]
        cls.stock_quant_obj = cls.env["stock.quant"]

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
            {"name": "Test Location", "usage": "internal", "discrepancy_threshold": 0.1}
        )
        cls.test_loc2 = cls.obj_location.create(
            {
                "name": "Test Location 2",
                "usage": "internal",
                "discrepancy_threshold": 0.1,
            }
        )
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
        cls.quant1 = cls.stock_quant_obj.create(
            {
                "location_id": cls.test_loc.id,
                "product_id": cls.product1.id,
                "inventory_quantity": 20.0,
            }
        )
        cls.quant1.action_apply_inventory()
        cls.quant2 = cls.stock_quant_obj.create(
            {
                "location_id": cls.test_loc.id,
                "product_id": cls.product2.id,
                "inventory_quantity": 30.0,
            }
        )
        cls.quant2.action_apply_inventory()
        cls.quant3 = cls.stock_quant_obj.create(
            {
                "location_id": cls.test_loc2.id,
                "product_id": cls.product1.id,
                "inventory_quantity": 20.0,
            }
        )
        cls.quant3.action_apply_inventory()
        cls.quant4 = cls.stock_quant_obj.create(
            {
                "location_id": cls.test_loc2.id,
                "product_id": cls.product2.id,
                "inventory_quantity": 30.0,
            }
        )
        cls.quant4.action_apply_inventory()
        cls.svr_obj = cls.obj_svr.create(
            {
                "state": "wait",
                "location_id": cls.test_loc.id,
                "company_id": cls.env.company.id,
                "product_id": cls.product1.id,
            }
        )
        cls.test_svr2 = cls.obj_svr.create(
            {
                "location_id": cls.test_loc.id,
                "state": "wait",
                "product_id": cls.product2.id,
            }
        )

    def test_01_svr_creation(self):
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

    def test_02_svr_creation(self):
        """Tests the creation of Slot Verification Requests."""
        inventory = self.obj_inventory.create(
            {
                "name": "Generate over discrepancy in both lines.",
                "product_selection": "manual",
                "location_ids": [(6, 0, [self.test_loc2.id])],
                "product_ids": [(6, 0, [self.product1.id, self.product2.id])],
            }
        )
        inventory.action_state_to_in_progress()
        self.assertEqual(
            inventory.state,
            "in_progress",
            "Inventory Adjustment not changing to Pending to " "Approve.",
        )
        previous_count = len(
            self.obj_svr.search([("location_id", "=", self.test_loc2.id)])
        )
        for quant in inventory.stock_quant_ids:
            quant.write({"inventory_quantity": 10.0})
            quant.action_request_verification()
        current_count = len(
            self.obj_svr.search([("location_id", "=", self.test_loc2.id)])
        )
        self.assertEqual(
            current_count, previous_count + 2, "Slot Verification Request not created."
        )
        # Test the method to open SVR from quants
        for quant in inventory.stock_quant_ids:
            quant.action_open_svr()

    def test_02_svr_workflow(self):
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

    def test_03_view_methods(self):
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

    def test_04_svr_full_workflow(self):
        test_svr = self.obj_svr.create(
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

    def test_05_user_permissions_on_svr(self):
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

    def test_06_action_view_methods(self):
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

    def test_07_involved_move_lines_compute(self):
        move = self.obj_move.create(
            {
                "name": "Test Move",
                "product_id": self.product1.id,
                "product_uom_qty": 10,
                "product_uom": self.product1.uom_id.id,
                "location_id": self.test_loc.id,
                "location_dest_id": self.test_loc.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        move_line = move.move_line_ids[0]
        test_svr = self.obj_svr.create(
            {
                "location_id": self.test_loc.id,
                "state": "wait",
                "product_id": self.product1.id,
            }
        )
        test_svr.action_confirm()
        self.assertEqual(
            test_svr.state, "open", "Slot Verification Request not confirmed properly."
        )
        self.assertIn(
            move_line,
            test_svr.involved_move_line_ids,
            "Move line not found in involved_move_line_ids",
        )

    def test_08_involved_quants_compute(self):
        self.quant3 = self.env["stock.quant"].create(
            {
                "location_id": self.test_loc.id,
                "product_id": self.product1.id,
                "quantity": 20.0,
            }
        )
        test_svr = self.obj_svr.create(
            {
                "location_id": self.test_loc.id,
                "state": "wait",
                "product_id": self.product1.id,
            }
        )
        test_svr.action_confirm()
        self.assertIn(
            self.quant3,
            test_svr.involved_quant_ids,
            "Quant3 not found in involved_quant_ids",
        )

    def test_action_request_verification_creates_svr(self):
        """Test that action_request_verification creates SVR when condition met."""
        quant = self.stock_quant_obj.create(
            {
                "location_id": self.test_loc.id,
                "product_id": self.product1.id,
                "quantity": 20.0,
            }
        )
        quant.discrepancy_threshold = 0.1
        quant.discrepancy_percent = 0.5
        self.assertTrue(quant.discrepancy_percent > quant.discrepancy_threshold)
        previous_count = self.obj_svr.search_count([("quant_id", "=", quant.id)])
        quant.action_request_verification()
        svr = self.obj_svr.search([("quant_id", "=", quant.id)])
        self.assertEqual(
            self.obj_svr.search_count([("quant_id", "=", quant.id)]),
            previous_count + 1,
            "SVR was not created by action_request_verification",
        )
        self.assertTrue(
            quant.requested_verification, "Quant should be marked as requested."
        )
        self.assertEqual(svr.location_id.id, quant.location_id.id)

    def test_compute_allow_svr_creation(self):
        """Test the computed field allow_svr_creation"""
        quant = self.stock_quant_obj.create(
            {
                "location_id": self.test_loc.id,
                "product_id": self.product1.id,
                "quantity": 25.0,
            }
        )

        # Test when percent > threshold
        quant.discrepancy_threshold = 0.2
        quant.discrepancy_percent = 0.6
        quant._compute_allow_svr_creation()
        self.assertTrue(
            quant.allow_svr_creation,
            "Expected allow_svr_creation to be True when percent > threshold",
        )
        # Test when percent <= threshold
        quant.discrepancy_threshold = 0.5
        quant.discrepancy_percent = 0.3
        quant._compute_allow_svr_creation()
        self.assertFalse(
            quant.allow_svr_creation,
            "Expected allow_svr_creation to be False when percent <= threshold",
        )

    def test_action_confirm(self):
        self.svr_obj.action_confirm()
        self.assertEqual(self.svr_obj.state, "open")

    def test_action_cancel(self):
        self.svr_obj.action_cancel()
        self.assertEqual(self.svr_obj.state, "cancelled")
        self.assertFalse(self.svr_obj.quant_id.requested_verification)

    def test_action_solved(self):
        self.svr_obj.action_solved()
        self.assertEqual(self.svr_obj.state, "done")
        self.assertFalse(self.svr_obj.quant_id.requested_verification)

    def test_action_create_inventory_adjustment(self):
        result = self.svr_obj.action_create_inventory_adjustment()
        self.assertIn("res_id", result)
        inventory = self.obj_inventory.browse(result["res_id"])
        self.assertEqual(
            inventory.name, f"Inventory Adjustment from {self.svr_obj.name}"
        )
        self.assertEqual(inventory.product_ids.ids, [self.product1.id])
        self.assertEqual(inventory.location_ids.ids, [self.test_loc.id])
        self.assertEqual(
            inventory.solving_slot_verification_request_id.id, self.svr_obj.id
        )

    def test_action_open_svr_from_location(self):
        test_location = self.env["stock.location"].create(
            {
                "name": "SVR Test Location",
                "usage": "internal",
            }
        )
        svr1 = self.obj_svr.create(
            {
                "location_id": test_location.id,
                "product_id": self.product1.id,
            }
        )
        self.env.cr.flush()
        test_location._invalidate_cache()
        result = test_location.action_open_svr()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["res_id"], svr1.id)
        self.assertIn("views", result)
        self.assertIn("type", result)
        self.assertEqual(result["type"], "ir.actions.act_window")

        self.obj_svr.create(
            {
                "location_id": test_location.id,
                "product_id": self.product2.id,
            }
        )
        self.env.cr.flush()
        test_location._invalidate_cache()
        result_multi = test_location.action_open_svr()
        self.assertIsInstance(result_multi, dict)
        self.assertIn("domain", result_multi)
        self.assertTrue(
            len(test_location.slot_verification_ids) > 1,
            "Should have more than one SVR linked",
        )
        self.assertEqual(result_multi.get("res_id"), 0)
        self.assertEqual(
            set(result_multi["domain"][0][2]),
            set(test_location.slot_verification_ids.ids),
        )
        self.assertEqual(result_multi["type"], "ir.actions.act_window")

    def test_action_open_svr_from_quant(self):
        test_loc_quant = self.env["stock.location"].create(
            {
                "name": "SVR Quant Location",
                "usage": "internal",
            }
        )
        quant = self.env["stock.quant"].create(
            {
                "location_id": test_loc_quant.id,
                "product_id": self.product1.id,
                "quantity": 10,
            }
        )
        svr1 = self.obj_svr.create(
            {
                "quant_id": quant.id,
                "product_id": self.product1.id,
                "location_id": test_loc_quant.id,
            }
        )
        self.env.cr.flush()
        quant._invalidate_cache()
        result = quant.action_open_svr()
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("res_id"), svr1.id)
        self.assertEqual(result.get("type"), "ir.actions.act_window")
        self.assertIn("views", result)

        self.obj_svr.create(
            {
                "quant_id": quant.id,
                "product_id": self.product2.id,
                "location_id": test_loc_quant.id,
            }
        )
        self.env.cr.flush()
        quant._invalidate_cache()
        result_multi = quant.action_open_svr()
        self.assertEqual(result_multi.get("type"), "ir.actions.act_window")
        self.assertIn("domain", result_multi)
        self.assertEqual(
            set(result_multi["domain"][0][2]), set(quant.slot_verification_ids.ids)
        )
        self.assertEqual(result_multi.get("res_id"), 0)

    def test_action_view_inventories(self):
        test_location = self.env["stock.location"].create(
            {
                "name": "SVR Test Location",
                "usage": "internal",
            }
        )
        inv1 = self.obj_inventory.create(
            {
                "name": "Test Inventory 1",
                "location_ids": [(6, 0, [test_location.id])],
            }
        )
        group1 = self.obj_svr.create(
            {
                "created_inventory_ids": [(6, 0, [inv1.id])],
                "location_id": test_location.id,
            }
        )

        self.env.cr.flush()
        group1._invalidate_cache()

        result_single = group1.action_view_inventories()

        self.assertEqual(result_single.get("res_id"), inv1.id)
        self.assertEqual(result_single.get("type"), "ir.actions.act_window")
        self.assertIn("views", result_single)

        inv2 = self.obj_inventory.create(
            {
                "name": "Test Inventory 2",
                "location_ids": [(6, 0, [test_location.id])],
            }
        )

        group1.write({"created_inventory_ids": [(4, inv2.id)]})
        self.env.cr.flush()
        group1._invalidate_cache()

        result_multi = group1.action_view_inventories()
        self.assertEqual(result_multi.get("type"), "ir.actions.act_window")
        self.assertIn("domain", result_multi)
        self.assertEqual(
            set(result_multi["domain"][0][2]), set(group1.created_inventory_ids.ids)
        )
        self.assertEqual(result_multi.get("res_id", 0), 0)

    def test_get_inventory_fields_create_extension(self):
        fields = self.stock_quant_obj._get_inventory_fields_create()
        self.assertIn(
            "slot_verification_ids",
            fields,
            "'slot_verification_ids' should be in the inventory fields returned",
        )
        self.assertIn(
            "requested_verification",
            fields,
            "'requested_verification' should be in the inventory fields returned",
        )

    def test_get_involved_move_lines_domain(self):
        svr = self.obj_svr.create(
            {
                "location_id": self.test_loc.id,
                "product_id": self.product1.id,
            }
        )
        domain = svr._get_involved_move_lines_domain()
        self.assertIsInstance(domain, list, "Domain must be a list")
        self.assertIn(("location_id", "=", self.test_loc.id), domain)
        self.assertIn(("location_dest_id", "=", self.test_loc.id), domain)
        self.assertIn(("product_id", "=", self.product1.id), domain)

        lot = self.env["stock.lot"].create(
            {
                "product_id": self.product1.id,
                "name": "LOT-001",
                "company_id": self.test_loc.company_id.id,
            }
        )
        svr_with_lot = self.obj_svr.create(
            {
                "location_id": self.test_loc.id,
                "product_id": self.product1.id,
                "lot_id": lot.id,
            }
        )
        domain_with_lot = svr_with_lot._get_involved_move_lines_domain()
        self.assertIn(
            ("lot_id", "=", lot.id),
            domain_with_lot,
            "Domain should include lot_id when set",
        )

    def test_get_involved_quants_domain(self):
        svr = self.obj_svr.create(
            {
                "location_id": self.test_loc.id,
                "product_id": self.product1.id,
            }
        )
        domain = svr._get_involved_quants_domain()
        self.assertIn(("location_id", "=", self.test_loc.id), domain)
        self.assertIn(("product_id", "=", self.product1.id), domain)
        self.assertNotIn(
            ("lot_id", "!=", False), domain, "lot_id should not be in domain if not set"
        )
        lot = self.env["stock.lot"].create(
            {
                "product_id": self.product1.id,
                "name": "LOT-001",
                "company_id": self.test_loc.company_id.id,
            }
        )
        svr_with_lot = self.obj_svr.create(
            {
                "location_id": self.test_loc.id,
                "product_id": self.product1.id,
                "lot_id": lot.id,
            }
        )
        domain_with_lot = svr_with_lot._get_involved_quants_domain()
        self.assertIn(
            ("lot_id", "=", lot.id),
            domain_with_lot,
            "Domain should include lot_id when provided",
        )

    def test_action_view_move_lines(self):
        move = self.obj_move.create(
            {
                "name": "Move for SVR",
                "product_id": self.product1.id,
                "product_uom_qty": 5,
                "product_uom": self.product1.uom_id.id,
                "location_id": self.test_loc.id,
                "location_dest_id": self.test_loc.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        move_line = move.move_line_ids[0]
        svr = self.obj_svr.create(
            {
                "location_id": self.test_loc.id,
                "product_id": self.product1.id,
                "state": "wait",
            }
        )
        svr.write({"involved_move_line_ids": [(6, 0, [move_line.id])]})
        action = svr.action_view_move_lines()
        self.assertIsInstance(action, dict, "Returned value should be a dictionary")
        self.assertIn("domain", action, "Action must include a domain")
        self.assertIn(
            ("id", "in", [move_line.id]),
            action["domain"],
            "Domain should filter by involved move lines",
        )

    def test_action_view_quants(self):
        quant = self.env["stock.quant"].create(
            {
                "location_id": self.test_loc.id,
                "product_id": self.product1.id,
                "quantity": 15.0,
            }
        )
        svr = self.obj_svr.create(
            {
                "location_id": self.test_loc.id,
                "product_id": self.product1.id,
                "state": "wait",
            }
        )
        svr.write({"involved_quant_ids": [(6, 0, [quant.id])]})
        action = svr.action_view_quants()
        self.assertIsInstance(action, dict, "Action must be a dictionary.")
        self.assertIn("domain", action, "Action should include a domain.")
        self.assertIn(
            ("id", "in", [quant.id]),
            action["domain"],
            "Domain must filter the correct quant ID.",
        )

    def test_09_product_related_fields(self):
        svr = self.obj_svr.create(
            {
                "location_id": self.test_loc.id,
                "state": "wait",
                "product_id": self.product1.id,
            }
        )
        self.assertEqual(
            svr.product_name, "Test Product 1", "Product name not set correctly in SVR."
        )
        self.assertEqual(
            svr.product_default_code,
            "PROD1",
            "Product default code not set correctly in SVR.",
        )

    def test_10_processed_by(self):
        svr = self.obj_svr.create(
            {
                "location_id": self.test_loc.id,
                "state": "wait",
                "product_id": self.product1.id,
            }
        )
        self.assertFalse(svr.processed_by)
        svr.action_confirm()
        self.assertFalse(
            svr.processed_by, "Processed By should remain empty after confirm."
        )
        svr.action_solved()
        self.assertEqual(
            svr.processed_by.id,
            self.env.uid,
            "Processed By not set correctly after solved action.",
        )
        svr_cancel = self.obj_svr.create(
            {
                "location_id": self.test_loc.id,
                "state": "wait",
                "product_id": self.product1.id,
            }
        )
        svr_cancel.action_confirm()
        self.assertFalse(
            svr_cancel.processed_by, "Processed By should remain empty after confirm."
        )
        svr_cancel.action_cancel()
        self.assertEqual(
            svr_cancel.processed_by.id,
            self.env.uid,
            "Processed By not set correctly after cancel action.",
        )
