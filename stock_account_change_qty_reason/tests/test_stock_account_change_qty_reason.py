# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestStockAccountChangeQtyReason(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockAccountChangeQtyReason, cls).setUpClass()

        # MODELS
        cls.product_product_model = cls.env["product.product"]
        cls.product_category_model = cls.env["product.category"]
        cls.wizard_model = cls.env["stock.change.product.qty"]
        cls.stock_inventory = cls.env["stock.inventory"]
        cls.preset_reason = cls.env["stock.inventory.line.reason"]

        # INSTANCES
        cls.stock_valuation_account = cls.env["account.account"].create(
            {
                "name": "Stock Valuation",
                "code": "Stock Valuation",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_current_assets"
                ).id,
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

        # Instance: account type (receivable)
        cls.type_recv = cls.env.ref("account.data_account_type_receivable")

        # Instance: account type (payable)
        cls.type_payable = cls.env.ref("account.data_account_type_payable")

        # account (receivable)
        cls.account_input = cls.env["account.account"].create(
            {
                "name": "test_account_reason_input",
                "code": "1234",
                "user_type_id": cls.type_recv.id,
                "company_id": company.id,
                "reconcile": True,
            }
        )

        # account (payable)
        cls.account_output = cls.env["account.account"].create(
            {
                "name": "test_account_reason_output",
                "code": "4321",
                "user_type_id": cls.type_payable.id,
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
        cls._product_change_qty(cls, cls.product, 10)
        cls.inventory = cls.stock_inventory.create(
            {
                "name": "Inventory Adjustment Product",
                "product_ids": [(4, cls.product.id)],
                "preset_reason_id": cls.reason.id,
            }
        )
        cls.inventory.action_start()

    def _create_product(self, name):
        return self.product_product_model.create(
            {
                "name": name,
                "categ_id": self.category.id,
                "type": "product",
                "standard_price": 100,
            }
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
        return self.preset_reason.create({"name": name, "description": description})

    def test_product_change_qty_account_input(self):
        # update qty on hand and add reason
        self.inventory.line_ids[0].write({"product_qty": 100})
        self.inventory.action_validate()

        # check stock moves and account moves created
        stock_move = self.env["stock.move"].search(
            [("product_id", "=", self.product.id), ("product_qty", "=", 90)]
        )
        account_move = self.env["account.move"].search(
            [("stock_move_id", "=", stock_move.id)]
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
        self.inventory.line_ids[0].write({"product_qty": 5})
        self.inventory.action_validate()

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
