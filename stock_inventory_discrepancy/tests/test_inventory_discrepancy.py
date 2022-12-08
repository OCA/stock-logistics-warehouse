# Copyright 2017-2020 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo_test_helper import FakeModelLoader

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestInventoryDiscrepancy(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestInventoryDiscrepancy, self).setUp(*args, **kwargs)
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.obj_wh = self.env["stock.warehouse"]
        self.obj_location = self.env["stock.location"]
        self.obj_inventory = self.env["stock.inventory"]
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
            {"name": "Test Location", "usage": "internal", "discrepancy_threshold": 0.1}
        )
        self.test_wh = self.obj_warehouse.create(
            {"name": "Test WH", "code": "T", "discrepancy_threshold": 0.2}
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
        self.user = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "user",
                "email": "test.user@example.com",
                "groups_id": [(6, 0, [group_stock_user.id])],
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

        quant_line1 = self.obj_quant.create(
            {
                "product_id": self.product1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "inventory_quantity": 2.0,
                "location_id": self.test_loc.id,
            }
        )
        quant_line2 = self.obj_quant.create(
            {
                "product_id": self.product2.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "inventory_quantity": 4.0,
                "location_id": self.test_loc.id,
            }
        )

        starting_inv = self.obj_inventory.create(
            {
                "name": "Starting inventory",
                "stock_quant_ids": [(6, 0, [quant_line1.id, quant_line2.id])],
            }
        )
        starting_inv.action_force_done()

    def test_compute_discrepancy(self):
        """Tests if the discrepancy is correctly computed."""
        quant_line3 = self.obj_quant.create(
            {
                "product_id": self.product1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "inventory_quantity": 3.0,
                "location_id": self.test_loc.id,
            }
        )
        quant_line4 = self.obj_quant.create(
            {
                "product_id": self.product2.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "inventory_quantity": 3.0,
                "location_id": self.test_loc.id,
            }
        )

        inventory = self.obj_inventory.create(
            {
                "name": "Test Discrepancy Computation",
                "location_ids": [(4, self.test_loc.id)],
                "stock_quant_ids": [(6, 0, [quant_line3.id, quant_line4.id])],
            }
        )
        with self.assertRaises(AssertionError):
            self.assertEqual(
                inventory.stock_quant_ids[0].discrepancy_qty,
                1.0,
                "Wrong Discrepancy qty computation.",
            )
            self.assertEqual(
                inventory.stock_quant_ids[1].discrepancy_qty,
                -1.0,
                "Wrong Discrepancy qty computation.",
            )

    def test_discrepancy_validation(self):
        """Tests the new workflow"""
        quant_line = self.obj_quant.create(
            {
                "product_id": self.product1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "inventory_quantity": 3.0,
                "location_id": self.test_loc.id,
            }
        )

        inventory = self.obj_inventory.create(
            {
                "name": "Test Forcing Validation Method",
                "location_ids": [(4, self.test_loc.id)],
                "stock_quant_ids": [(6, 0, [quant_line.id])],
            }
        )
        self.assertEqual(
            inventory.state, "draft", "Testing Inventory wrongly configurated"
        )
        self.assertEqual(
            inventory.stock_quant_ids.discrepancy_threshold,
            0.1,
            "Threshold wrongly computed in Inventory Line.",
        )
        with self.assertRaises(ValidationError):
            inventory.with_user(self.user).action_state_to_in_progress()
        with self.assertRaises(AccessError):
            inventory.with_user(self.user).action_state_to_done()
        self.assertTrue(inventory.stock_quant_ids.has_over_discrepancy)
        self.assertEqual(
            inventory.over_discrepancy_line_count,
            1,
            "Computation of over-discrepancies failed.",
        )
        with self.assertRaises(AssertionError):
            self.assertEqual(
                inventory.state,
                "pending",
                "Inventory Adjustment not changing to Pending to " "Approve.",
            )
        with self.assertRaises(UserError):
            inventory.with_user(self.manager).action_force_done()
        with self.assertRaises(AssertionError):
            self.assertEqual(
                inventory.state,
                "done",
                "Forcing the validation of the inventory adjustment "
                "not working properly.",
            )

    def test_discrepancy_validation_always(self):
        """Tests the new workflow"""
        quant_line = self.obj_quant.create(
            {
                "product_id": self.product1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "inventory_quantity": 3.0,
                "location_id": self.test_loc.id,
            }
        )
        inventory = self.obj_inventory.create(
            {
                "name": "Test Forcing Validation Method",
                "location_ids": [(4, self.test_loc.id)],
                "stock_quant_ids": [(6, 0, [quant_line.id])],
            }
        )
        self.assertEqual(
            inventory.state, "draft", "Testing Inventory wrongly configurated"
        )
        self.assertEqual(
            inventory.stock_quant_ids.discrepancy_threshold,
            0.1,
            "Threshold wrongly computed in Inventory Line.",
        )
        with self.assertRaises(ValidationError):
            inventory.with_user(self.user_2).action_state_to_in_progress()
        # User with no privileges can't validate a Inventory Adjustment.
        with self.assertRaises(UserError):
            inventory.with_user(self.no_user).action_state_to_done()
            inventory.with_user(self.user_2).action_state_to_done()
        self.assertEqual(
            inventory.over_discrepancy_line_count,
            1,
            "Computation of over-discrepancies failed.",
        )
        with self.assertRaises(AssertionError):
            self.assertEqual(
                inventory.state,
                "done",
                "Stock Managers belongs to group Validate All inventory Adjustments",
            )

    def test_warehouse_threshold(self):
        """Tests the behaviour if the threshold is set on the WH."""
        quant_line = self.obj_quant.create(
            {
                "product_id": self.product1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "inventory_quantity": 3.0,
                "location_id": self.test_wh.lot_stock_id.id,
            }
        )
        inventory = self.obj_inventory.create(
            {
                "name": "Test Threshold Defined in WH",
                "location_ids": [(4, self.test_wh.view_location_id.id)],
                "stock_quant_ids": [(6, 0, [quant_line.id])],
            }
        )
        self.assertEqual(
            inventory.stock_quant_ids.discrepancy_threshold,
            0.2,
            "Threshold wrongly computed in Inventory Line.",
        )

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
