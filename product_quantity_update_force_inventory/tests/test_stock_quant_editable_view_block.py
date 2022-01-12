# Copyright 2020 Forgeflow, S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockQuantEditableViewBlock(TransactionCase):
    def setUp(self):
        super(TestStockQuantEditableViewBlock, self).setUp()
        self.inventory_model = self.env["stock.inventory"]
        self.res_users_model = self.env["res.users"]
        self.company = self.env.ref("base.main_company")
        self.grp_stock_manager = self.env.ref("stock.group_stock_manager")

        self.user = self.res_users_model.create(
            {
                "name": "Test Account User",
                "login": "user_1",
                "email": "example@yourcompany.com",
                "password": "password",
                "company_id": self.company.id,
                "company_ids": [(4, self.company.id)],
                "groups_id": [(6, 0, [self.grp_stock_manager.id])],
            }
        )
        self.product_product = self.env.ref("product.product_product_4")
        self.product_template = self.product_product.product_tmpl_id

        self.stock_quant_editable_tree_view = self.env.ref(
            "stock.view_stock_quant_tree_editable"
        )

    def test_stock_quant_editable_view_block(self):
        """Check if clicking On hand Smart Button on Product Card
        does not send user to editable stock quant view"""
        action_pp = self.product_product.with_user(self.user).action_open_quants()
        self.assertNotEqual(
            self.stock_quant_editable_tree_view.id,
            action_pp["view_id"],
            "Editable Stock Quant View is still prompting on Product Product",
        )

        action_pt = self.product_template.with_user(self.user).action_open_quants()
        self.assertNotEqual(
            self.stock_quant_editable_tree_view.id,
            action_pt["view_id"],
            "Editable Stock Quant View is still prompting on Product Template",
        )

    def test_update_quantity_triggers_inventory_adjustment(self):
        action_pp = self.product_product.with_user(
            self.user
        ).action_update_quantity_on_inventory_adjustment()
        self.assertIn(
            self.product_product.display_name, action_pp["context"]["default_name"]
        )
        self.assertEqual(
            action_pp["context"]["default_product_ids"],
            [(6, 0, self.product_product.ids)],
        )
        action_pt = self.product_template.with_user(
            self.user
        ).action_update_quantity_on_inventory_adjustment()
        self.assertIn(
            self.product_template.display_name, action_pt["context"]["default_name"]
        )
        self.assertEqual(
            action_pt["context"]["default_product_ids"],
            [(6, 0, self.product_template.product_variant_ids.ids)],
        )
