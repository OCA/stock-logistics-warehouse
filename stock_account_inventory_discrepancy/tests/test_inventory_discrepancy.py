# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import except_orm
from odoo.tests.common import TransactionCase


class TestInventoryDiscrepancy(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.obj_wh = self.env["stock.warehouse"]
        self.obj_location = self.env["stock.location"]
        self.obj_inventory = self.env["stock.inventory"]
        self.obj_product = self.env["product.product"]
        self.obj_warehouse = self.env["stock.warehouse"]
        self.obj_upd_qty_wizard = self.env["stock.change.product.qty"]

        self.product1 = self.obj_product.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "default_code": "PROD1",
                "standard_price": 110.0,
            }
        )
        self.product2 = self.obj_product.create(
            {
                "name": "Test Product 2",
                "type": "product",
                "default_code": "PROD2",
                "standard_price": 150.0,
            }
        )
        self.test_loc = self.obj_location.create(
            {
                "name": "Test Location",
                "usage": "internal",
                "discrepancy_amount_threshold": 100,
            }
        )
        self.test_wh = self.obj_warehouse.create(
            {"name": "Test WH", "code": "T", "discrepancy_amount_threshold": 300}
        )
        self.obj_location._parent_store_compute()

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

        starting_inv = self.obj_inventory.create(
            {
                "name": "Starting inventory",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "product_qty": 2.0,
                            "location_id": self.test_loc.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product2.id,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "product_qty": 4.0,
                            "location_id": self.test_loc.id,
                        },
                    ),
                ],
            }
        )
        starting_inv.action_force_done()

    def test_compute_discrepancy(self):
        """Tests if the amount discrepancy is correctly computed.
        """
        inventory = self.obj_inventory.create(
            {
                "name": "Test Discrepancy Computation",
                "location_ids": [(6, 0, self.test_loc.ids)],
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "product_qty": 3.0,
                            "location_id": self.test_loc.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product2.id,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "product_qty": 3.0,
                            "location_id": self.test_loc.id,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(inventory.line_ids[0].discrepancy_amount, 110.0)
        self.assertEqual(inventory.line_ids[1].discrepancy_amount, -150.0)

    def test_amount_discrepancy_validation(self):
        """Tests the workflow with amount threshold."""
        inventory = self.obj_inventory.create(
            {
                "name": "Test Forcing Validation Method",
                "location_ids": [(6, 0, self.test_loc.ids)],
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "product_qty": 3.0,
                            "location_id": self.test_loc.id,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(inventory.state, "draft")
        inventory.action_start()
        self.assertEqual(inventory.line_ids.discrepancy_amount_threshold, 100)
        self.assertTrue(inventory.line_ids[0].has_over_discrepancy)
        inventory.with_user(self.user).with_context(
            {"normal_view": True}
        ).action_validate()
        self.assertEqual(inventory.over_discrepancy_line_count, 1)
        self.assertEqual(inventory.state, "pending")

    def test_warehouse_amount_threshold(self):
        """Tests the behaviour if the threshold is set on the WH."""
        inventory = self.obj_inventory.create(
            {
                "name": "Test Threshold Defined in WH",
                "location_ids": [(6, 0, self.test_wh.view_location_id.ids)],
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "product_qty": 3.0,
                            "location_id": self.test_wh.lot_stock_id.id,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(inventory.line_ids.discrepancy_amount_threshold, 300)

    def test_update_qty_user_error_amount(self):
        """Test if a user error raises when a stock user tries to update the
        qty for a product and the correction is a discrepancy over the
        threshold."""
        upd_qty = self.obj_upd_qty_wizard.with_user(self.user).create(
            {
                "product_id": self.product1.id,
                "product_tmpl_id": self.product1.product_tmpl_id.id,
                "new_quantity": 10.0,
            }
        )
        # Since v13, stock users are not allowed to update product qty
        # (AccessError, standard) but if access are modified to allow them,
        # they will not be able to surpass the threshold (UserError
        # added in this module).
        with self.assertRaises(except_orm):
            upd_qty.change_product_qty()
