# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common, new_test_user


class TestStockRequestPurchaseRequest(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(
            context=dict(
                self.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
            )
        )
        # common models
        self.stock_request = self.env["stock.request"]

        # refs
        self.main_company = self.env.ref("base.main_company")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.categ_unit = self.env.ref("uom.product_uom_categ_unit")

        # common data
        self.company_2 = self.env["res.company"].create({"name": "Comp2"})
        self.wh2 = self.env["stock.warehouse"].search(
            [("company_id", "=", self.company_2.id)], limit=1
        )
        self.stock_request_user = new_test_user(
            self.env,
            login="stock_request_user",
            groups="stock_request.group_stock_request_user",
            company_ids=[(6, 0, [self.main_company.id, self.company_2.id])],
        )
        self.stock_request_manager = new_test_user(
            self.env,
            login="stock_request_manager",
            groups="stock_request.group_stock_request_manager",
            company_ids=[(6, 0, [self.main_company.id, self.company_2.id])],
        )
        self.route_buy = self.warehouse.buy_pull_id.route_id
        self.supplier = self.env["res.partner"].create({"name": "Supplier"})
        self.product = self._create_product("SH", "Shoes", False)

        self.uom_dozen = self.env["uom.uom"].create(
            {
                "name": "Test-DozenA",
                "category_id": self.categ_unit.id,
                "factor_inv": 12,
                "uom_type": "bigger",
                "rounding": 0.001,
            }
        )

    def _create_product(self, default_code, name, company_id):
        return self.env["product.product"].create(
            {
                "name": name,
                "default_code": default_code,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "company_id": company_id,
                "type": "product",
                "route_ids": [(6, 0, self.route_buy.ids)],
                "seller_ids": [(0, 0, {"name": self.supplier.id, "delay": 5})],
                "purchase_request": True,
            }
        )

    def test_create_request_01(self):
        """Single Stock request with buy rule"""
        expected_date = fields.Datetime.now()
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": expected_date,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "company_id": self.main_company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.warehouse.lot_stock_id.id,
                        "expected_date": expected_date,
                    },
                )
            ],
        }

        order = (
            self.env["stock.request.order"]
            .with_user(self.stock_request_user)
            .create(vals)
        )

        order.action_confirm()

        self.assertEqual(order.state, "open")
        self.assertEqual(order.stock_request_ids.state, "open")

        order.refresh()

        self.assertEqual(len(order.sudo().purchase_request_ids), 1)
        self.assertEqual(len(order.picking_ids), 0)
        self.assertEqual(len(order.move_ids), 0)
        self.assertEqual(len(order.stock_request_ids.sudo().purchase_request_ids), 1)
        self.assertEqual(len(order.stock_request_ids.picking_ids), 0)
        self.assertEqual(len(order.stock_request_ids.move_ids), 0)
        self.assertEqual(order.stock_request_ids.qty_in_progress, 0.0)

        purchase_request = order.sudo().purchase_request_ids[0]
        stock_request = purchase_request.sudo().stock_request_ids[0]

        self.assertEqual(
            purchase_request.company_id, order.stock_request_ids[0].company_id
        )
        purchase_request.refresh()
        self.assertEqual(len(purchase_request.sudo().line_ids), 1)

        purchase_request_line = purchase_request.sudo().line_ids[0]
        self.assertEqual(purchase_request_line.product_id, self.product)
        self.assertEqual(purchase_request_line.product_qty, 5.0)

        order.sudo().purchase_request_ids.company_id = self.company_2

        with self.assertRaises(ValidationError):
            stock_request.sudo()._check_purchase_request_company_constrains()

        with self.assertRaises(ValidationError):
            purchase_request_line.sudo()._check_purchase_request_company_constrains()

        order.sudo().purchase_request_ids.company_id = self.main_company

        # Purchase Request in stock.request.order

        action = order.action_view_purchase_request()
        purchase_requests = order.purchase_request_ids

        self.assertEqual(action.get("type"), "ir.actions.act_window")
        self.assertEqual(
            action.get("xml_id"), "purchase_request.purchase_request_form_action"
        )

        self.assertCountEqual(
            action.get("domain", []),
            [("id", "in", purchase_requests.ids)],
        ) if len(purchase_requests) > 1 else None

        self.assertEqual(
            action.get("views"),
            [(self.env.ref("purchase_request.view_purchase_request_form").id, "form")],
        )
        self.assertEqual(
            action.get("res_id"), purchase_requests.id
        ) if purchase_requests else (
            self.assertNotIn("domain", action),
            self.assertNotIn("res_id", action),
        )

        # Stock Request in purchase.request

        action = purchase_request.action_view_stock_request()
        requests = purchase_request._get_stock_requests()

        self.assertEqual(action.get("type"), "ir.actions.act_window")
        self.assertEqual(
            action.get("xml_id"), "stock_request.action_stock_request_form"
        )
        self.assertEqual(
            action.get("views"),
            [(self.env.ref("stock_request.view_stock_request_form").id, "form")],
        )
        self.assertEqual(action.get("res_id"), requests.id)

        # Purchase Request in stock.request

        action = stock_request.action_view_purchase_request()
        purchase_requests = stock_request.purchase_request_ids

        self.assertEqual(action.get("type"), "ir.actions.act_window")
        self.assertEqual(
            action.get("xml_id"), "purchase_request.purchase_request_form_action"
        )
        self.assertCountEqual(
            action.get("domain", []),
            [("id", "in", purchase_requests.ids)],
        ) if len(purchase_requests) > 1 else None

        self.assertEqual(
            action.get("views"),
            [(self.env.ref("purchase_request.view_purchase_request_form").id, "form")],
        )
        self.assertEqual(
            action.get("res_id"), purchase_requests.id
        ) if purchase_requests else (
            self.assertNotIn("domain", action),
            self.assertNotIn("res_id", action),
        )

        self.assertEqual(order.sudo().purchase_request_ids.stock_request_count, 1)
        stock_requests = order.sudo().purchase_request_ids._get_stock_requests()
        self.assertEqual(len(stock_requests), 1)
        self.assertEqual(stock_requests[0].id, order.sudo().stock_request_ids.id)

    def test_cancel_request(self):
        """Test cancellation of Stock Request."""
        expected_date = fields.Datetime.now()
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": expected_date,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "company_id": self.main_company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.warehouse.lot_stock_id.id,
                        "expected_date": expected_date,
                    },
                )
            ],
        }

        order = (
            self.env["stock.request.order"]
            .with_user(self.stock_request_user)
            .create(vals)
        )

        order.action_confirm()
        order.action_cancel()

        self.assertEqual(order.state, "cancel")
        self.assertTrue(
            all(
                purchase_request.state == "rejected"
                for purchase_request in order.sudo().purchase_request_ids
            )
        )
