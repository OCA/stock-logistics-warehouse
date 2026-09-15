# Copyright 2017-2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.stock_request.tests.test_stock_request import TestStockRequest


class TestStockRequestAnalytic(TestStockRequest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AccountAnalyticAccount = cls.env["account.analytic.account"]
        cls.AccountAnalyticPlan = cls.env["account.analytic.plan"]
        # Data
        cls.expected_date = fields.Datetime.now()
        cls.plan = cls.AccountAnalyticPlan.create({"name": "Plan 1"})
        cls.plan2 = cls.AccountAnalyticPlan.create(
            {
                "name": "Plan 2",
                "company_id": cls.company_2.id,
            }
        )
        cls.analytic1 = cls.AccountAnalyticAccount.create(
            {"name": "Analytic", "plan_id": cls.plan.id}
        )
        cls.analytic2 = cls.AccountAnalyticAccount.create(
            {
                "name": "Analytic",
                "company_id": cls.company_2.id,
                "plan_id": cls.plan2.id,
            }
        )
        cls.analytic3 = cls.AccountAnalyticAccount.create(
            {"name": "Analytic 3", "plan_id": cls.plan.id}
        )
        cls.product2 = cls._create_product("SH", "Shoes2", False)
        supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.test_route = cls.env["stock.route"].create(
            {
                "name": "Test Stock Request Analytic Route",
                "product_selectable": True,
                "product_categ_selectable": False,
                "warehouse_selectable": True,
                "warehouse_ids": [(4, cls.warehouse.id)],
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Replenish WH/Stock from Suppliers",
                            "action": "pull",
                            "picking_type_id": cls.warehouse.in_type_id.id,
                            "location_src_id": supplier_location.id,
                            "location_dest_id": cls.warehouse.lot_stock_id.id,
                            "procure_method": "make_to_stock",
                        },
                    )
                ],
            }
        )
        cls.product.route_ids = [(4, cls.test_route.id)]
        cls.product2.route_ids = [(4, cls.test_route.id)]

    def prepare_order_request_analytic(self, request_data):
        return {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": self.expected_date,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "product_uom_id": product.uom_id.id,
                        "product_uom_qty": qty,
                        "analytic_distribution": analytic_distribution,
                        "company_id": self.main_company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.warehouse.lot_stock_id.id,
                        "expected_date": self.expected_date,
                    },
                )
                for (product, qty, analytic_distribution) in request_data
            ],
        }

    def test_stock_analytic_01(self):
        vals = self.prepare_order_request_analytic(
            [(self.product, 5, {self.analytic1.id: 100})]
        )
        order = self.request_order.create(vals)
        req = order.stock_request_ids
        order.action_confirm()
        self.assertEqual(
            req.move_ids.mapped("analytic_distribution"),
            [{str(self.analytic1.id): 100}],
        )

    def test_stock_analytic_02(self):
        vals = self.prepare_order_request_analytic(
            [(self.product, 5, {self.analytic1.id: 50, self.analytic3.id: 50})]
        )
        order = self.request_order.create(vals)
        req = order.stock_request_ids
        order.action_confirm()
        self.assertEqual(
            req.move_ids.mapped("analytic_distribution"),
            [{str(self.analytic1.id): 50, str(self.analytic3.id): 50}],
        )

    def test_stock_multi_analytic(self):
        vals = self.prepare_order_request_analytic(
            [
                (self.product, 5, {self.analytic1.id: 100}),
                (self.product2, 5, {self.analytic2.id: 20, self.analytic3.id: 80}),
            ]
        )
        order = self.request_order.create(vals)
        req_product = order.stock_request_ids.filtered(
            lambda x: x.product_id == self.product
        )
        req_product2 = order.stock_request_ids.filtered(
            lambda x: x.product_id == self.product2
        )
        order.action_confirm()
        self.assertEqual(
            req_product.move_ids.mapped("analytic_distribution"),
            [{str(self.analytic1.id): 100}],
        )
        self.assertEqual(
            req_product2.move_ids.mapped("analytic_distribution"),
            [{str(self.analytic2.id): 20, str(self.analytic3.id): 80}],
        )

    def test_order_compute_analytic_fields(self):
        vals = self.prepare_order_request_analytic(
            [
                (self.product, 5, {self.analytic1.id: 100}),
                (self.product2, 3, {self.analytic3.id: 100}),
            ]
        )
        order = self.request_order.create(vals)

        self.assertSetEqual(
            set(order.analytic_account_ids.ids),
            {self.analytic1.id, self.analytic3.id},
        )
        self.assertEqual(order.analytic_count, 2)

    def test_action_view_analytic_account_single(self):
        vals = self.prepare_order_request_analytic(
            [(self.product, 5, {self.analytic1.id: 100})]
        )
        order = self.request_order.create(vals)
        action = order.with_context(
            analytic_type="analytic_account"
        ).action_view_analytic()

        self.assertEqual(action["res_id"], self.analytic1.id)
        self.assertIn("views", action)

    def test_action_view_analytic_account_multiple(self):
        vals = self.prepare_order_request_analytic(
            [
                (self.product, 5, {self.analytic1.id: 100}),
                (self.product2, 5, {self.analytic3.id: 100}),
            ]
        )
        order = self.request_order.create(vals)
        action = order.with_context(
            analytic_type="analytic_account"
        ).action_view_analytic()

        self.assertEqual(
            action.get("domain"),
            [("id", "in", [self.analytic1.id, self.analytic3.id])],
        )

    def test_action_view_stock_request_empty(self):
        action = self.analytic1.action_view_stock_request()
        self.assertIsInstance(action, dict)
        self.assertEqual(action.get("type"), "ir.actions.act_window")
