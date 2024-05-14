# Copyright 2019-2024 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockAccountChangeQtyReason(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_product_model = cls.env["product.product"]
        cls.product_category_model = cls.env["product.category"]
        cls.stock_quant = cls.env["stock.quant"]
        cls.preset_reason = cls.env["stock.quant.reason"]
        cls.Account = cls.env["account.account"]
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        # INSTANCES
        cls.stock_valuation_account = cls.env["account.account"].create(
            {
                "name": "Stock Valuation",
                "code": "StockValuation",
                "account_type": "asset_current",
            }
        )
        cls.category = cls.product_category_model.create(
            {
                "name": "Physical (test)",
                "property_cost_method": "standard",
                "property_valuation": "real_time",
                "property_stock_valuation_account_id": cls.stock_valuation_account,
            }
        )

        company = cls.env.ref("base.main_company")

        # account (receivable)
        cls.account_input = cls.env["account.account"].create(
            {
                "name": "test_account_reason_input",
                "code": "1234",
                "account_type": "asset_receivable",
                "company_id": company.id,
                "reconcile": True,
            }
        )

        # account (payable)
        cls.account_output = cls.env["account.account"].create(
            {
                "name": "test_account_reason_output",
                "code": "4321",
                "account_type": "liability_payable",
                "company_id": company.id,
                "reconcile": True,
            }
        )

        cls.reason = cls.preset_reason.create(
            {
                "name": "Test Reason",
                "description": "Test Reason Description",
                "account_reason_input_id": cls.account_input.id,
                "account_reason_output_id": cls.account_output.id,
            }
        )

        # Start Inventory with 10 units
        cls.product = cls._create_product(cls, "product_product")
        cls.inventory = cls.stock_quant.create(
            {
                "product_id": cls.product.id,
                "preset_reason_id": cls.reason.id,
                "location_id": cls.stock_location.id,
                "inventory_quantity": 10,
            }
        )
        cls.inventory.action_apply_inventory()

    def _create_product(self, name):
        return self.product_product_model.create(
            {
                "name": name,
                "categ_id": self.category.id,
                "type": "product",
                "standard_price": 100,
            }
        )

    def _create_reason(self, name, description=None):
        return self.preset_reason.create({"name": name, "description": description})

    def test_product_change_qty_account_input(self):
        # update qty on hand and add reason
        self.inventory.preset_reason_id = self.reason
        self.inventory.write({"inventory_quantity": 100})
        self.inventory.action_apply_inventory()

        # check stock moves and account moves created
        stock_move_line = self.env["stock.move.line"].search(
            [("product_id", "=", self.product.id), ("quantity", "=", 90)]
        )
        account_move = self.env["account.move"].search(
            [("stock_move_id", "=", stock_move_line.move_id.id)]
        )

        # asserts
        account_move_line1 = self.env["account.move.line"].search(
            [
                ("move_id", "=", account_move.id),
                ("account_id", "=", self.account_input.id),
            ]
        )
        account_move_line2 = self.env["account.move.line"].search(
            [
                ("move_id", "=", account_move.id),
                ("account_id", "=", self.stock_valuation_account.id),
            ]
        )
        self.assertEqual(
            abs(account_move_line1.balance), abs(account_move_line2.balance)
        )

    def test_product_change_qty_account_output(self):
        # update qty on hand and add reason
        self.inventory.preset_reason_id = self.reason
        self.inventory.write({"inventory_quantity": 5})
        self.inventory.action_apply_inventory()

        # check stock moves and account moves created
        stock_move = self.env["stock.move"].search(
            [("product_id", "=", self.product.id), ("product_qty", "=", 5)]
        )
        account_move = self.env["account.move"].search(
            [("stock_move_id", "=", stock_move.id)]
        )

        # asserts
        account_move_line3 = self.env["account.move.line"].search(
            [
                ("move_id", "=", account_move.id),
                ("account_id", "=", self.account_output.id),
            ]
        )
        account_move_line4 = self.env["account.move.line"].search(
            [
                ("move_id", "=", account_move.id),
                ("account_id", "=", self.stock_valuation_account.id),
            ]
        )
        self.assertEqual(
            abs(account_move_line3.balance), abs(account_move_line4.balance)
        )
