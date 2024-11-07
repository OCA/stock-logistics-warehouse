# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase, new_test_user, users

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestStockInventorySecurity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Lazy tests compatibility with `stock_inventory_discrepancy`
        cls.env = cls.env(context=dict(cls.env.context, skip_exceeded_discrepancy=True))
        # Create test records
        cls.inventory_user = new_test_user(
            cls.env,
            login="inventory",
            groups="stock_inventory_security.group_inventory_adjustment",
        )
        cls.stock_user = new_test_user(
            cls.env,
            login="stock",
            groups="stock.group_stock_user",
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "product",
            }
        )
        cls.product_lot = cls.env["stock.lot"].create(
            {
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.product_quants = (
            cls.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": cls.product.id,
                    "inventory_quantity": 4,
                    "lot_id": cls.product_lot.id,
                    "location_id": cls.stock_location.id,
                }
            )
        )
        cls.product_quants.action_apply_inventory()

    @users("inventory", "admin")
    def test_inventory_user_product_action_open_quants(self):
        """Test that the inventory user gets into inventory mode from products"""
        res = self.product.with_user(self.env.user).action_open_quants()
        self.assertFalse(res["context"].get("search_default_my_count"))

    @users("stock")
    def test_stock_user_product_action_open_quants(self):
        """Test that the stock user does not get into inventory mode from products"""
        res = self.product.with_user(self.env.user).action_open_quants()
        self.assertTrue(res["context"].get("search_default_my_count"))

    @users("inventory", "admin")
    def test_inventory_user_quant_action(self):
        """Test that the inventory user gets into inventory mode from quants"""
        res = self.product_quants.with_user(self.env.user).action_view_inventory()
        self.assertFalse(res["context"].get("search_default_my_count"))

    @users("stock")
    def test_stock_user_quant_action(self):
        """Test that the stock user does not get into inventory mode from quants"""
        res = self.product_quants.with_user(self.env.user).action_view_inventory()
        self.assertTrue(res["context"].get("search_default_my_count"))

    @users("inventory", "admin")
    def test_inventory_user_lot_action(self):
        """Test that the inventory user gets into inventory mode from lots"""
        res = self.product_lot.with_user(self.env.user).action_lot_open_quants()
        self.assertEqual(
            res["view_id"], self.env.ref("stock.view_stock_quant_tree_editable").id
        )
        self.assertTrue(res["context"].get("inventory_mode"))

    @users("stock")
    def test_stock_user_lot_action(self):
        """Test that the stock user does not get into inventory mode from lots"""
        res = self.product_lot.with_user(self.stock_user).action_lot_open_quants()
        self.assertEqual(res["view_id"], self.env.ref("stock.view_stock_quant_tree").id)
        self.assertFalse(res["context"].get("inventory_mode"))

    @users("inventory", "admin")
    def test_inventory_user_apply_inventory(self):
        """Test that the inventory user can apply inventory"""
        quant = (
            self.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": self.product.id,
                    "inventory_quantity": 10,
                    "lot_id": self.product_lot.id,
                    "location_id": self.stock_location.id,
                }
            )
        )
        quant.action_apply_inventory()
        self.assertEqual(self.product.qty_available, 10)

    @users("stock")
    def test_stock_user_apply_inventory(self):
        """Test that the stock user cannot apply inventory"""
        with self.assertRaisesRegex(
            UserError, "Only a stock manager can validate an inventory adjustment."
        ):
            quant = self.env["stock.quant"].create(
                {
                    "product_id": self.product.id,
                    "inventory_quantity": 10,
                    "lot_id": self.product_lot.id,
                    "location_id": self.stock_location.id,
                }
            )
            quant.action_apply_inventory()

    @users("inventory", "admin")
    def test_inventory_user_apply_inventory_reason(self):
        """Test that the inventory user can apply inventory with a reason"""
        quant = (
            self.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": self.product.id,
                    "lot_id": self.product_lot.id,
                    "location_id": self.stock_location.id,
                    "inventory_quantity": 10,
                }
            )
        )
        form_wizard = Form(
            self.env["stock.inventory.adjustment.name"].with_context(
                default_quant_ids=quant.ids
            )
        )
        form_wizard.inventory_adjustment_name = "Inventory Adjustment - Test"
        form_wizard.save().action_apply()
        self.assertTrue(
            self.env["stock.move"].search(
                [("reference", "=", "Inventory Adjustment - Test")], limit=1
            )
        )
        self.assertEqual(self.product.qty_available, 10)
