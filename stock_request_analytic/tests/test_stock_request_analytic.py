# Copyright 2017-2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import Command, fields
from odoo.exceptions import UserError
from odoo.tests import Form, common, new_test_user
from odoo.tests.common import users


class TestStockRequestAnalytic(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AccountAnalyticAccount = cls.env["account.analytic.account"]
        cls.ProductProduct = cls.env["product.product"]
        cls.StockRequest = cls.env["stock.request"]
        cls.StockRequestOrder = cls.env["stock.request.order"]
        cls.StockLocation = cls.env["stock.location"]

        cls.expected_date = fields.Datetime.now()
        cls.main_company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env.ref("stock.warehouse0")

        cls.demand_loc = cls.StockLocation.create(
            {
                "name": "Demand Location",
                "location_id": cls.warehouse.lot_stock_id.id,
                "usage": "internal",
            }
        )
        cls.AnalyticPlan = cls.env["account.analytic.plan"]
        cls.plan = cls.AnalyticPlan.create(
            {
                "name": "Main Analytic Plan",
            }
        )
        cls.analytic1 = cls.AccountAnalyticAccount.create(
            {
                "name": "A1",
                "plan_id": cls.plan.id,
            }
        )
        cls.analytic2 = cls.AccountAnalyticAccount.create(
            {
                "name": "A2",
                "plan_id": cls.plan.id,
            }
        )
        cls.analytic3 = cls.AccountAnalyticAccount.create(
            {
                "name": "A3",
                "plan_id": cls.plan.id,
            }
        )
        cls.product = cls.ProductProduct.create(
            {
                "name": "Test Product",
                "type": "service",
                "is_storable": True,
            }
        )
        new_test_user(
            cls.env,
            login="stock_request_user",
            groups="{}, {}, {}".format(
                "stock_request.group_stock_request_user",
                "analytic.group_analytic_accounting",
                "stock.group_stock_user",
            ),
            company_ids=[(6, 0, [cls.main_company.id])],
        )

    def prepare_order_request_analytic(self, analytic, company):
        analytic_distribution = {str(analytic.id): 100.0}
        vals = {
            "company_id": company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.demand_loc.id,
            "expected_date": self.expected_date,
            "stock_request_ids": [
                Command.create(
                    {
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "analytic_distribution": analytic_distribution,
                        "company_id": company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.demand_loc.id,
                        "expected_date": self.expected_date,
                    },
                )
            ],
        }
        return vals

    def prepare_order_request_multi_analytic(self, a1, a2, company):
        vals = {
            "company_id": company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.demand_loc.id,
            "expected_date": self.expected_date,
            "stock_request_ids": [
                Command.create(
                    {
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "analytic_distribution": {str(a1.id): 100.0},
                        "company_id": company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.demand_loc.id,
                        "expected_date": self.expected_date,
                    },
                ),
                Command.create(
                    {
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "analytic_distribution": {str(a2.id): 100.0},
                        "company_id": company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.demand_loc.id,
                        "expected_date": self.expected_date,
                    },
                ),
            ],
        }
        return vals

    def test_stock_analytic(self):
        vals = self.prepare_order_request_analytic(self.analytic1, self.main_company)
        order = self.StockRequestOrder.create(vals)
        req = order.stock_request_ids
        order.action_confirm()
        moves = req.move_ids
        for move in moves:
            self.assertEqual(
                move.analytic_distribution,
                {str(self.analytic1.id): 100.0},
                "La distribución analítica no se propagó correctamente al movimiento.",
            )
        self.assertEqual(order.analytic_count, 1)
        action = order.action_view_analytic()
        self.assertIn(self.analytic1.id, action["domain"][0][2])
        action2 = self.analytic1.action_view_stock_request()
        self.assertIn(order.id, action2["domain"][0][2])

    def test_stock_multi_analytic(self):
        vals = self.prepare_order_request_multi_analytic(
            self.analytic1, self.analytic3, self.main_company
        )
        order = self.StockRequestOrder.create(vals)
        order.action_confirm()
        self.assertEqual(
            order.analytic_count,
            2,
            "analytic_count no calculó correctamente para múltiples analíticas.",
        )

    def test_company(self):
        analytic_other_company = self.AccountAnalyticAccount.create(
            {
                "name": "X",
                "company_id": False,
                "plan_id": self.plan.id,
            }
        )
        with self.assertRaises(UserError):
            vals = self.prepare_order_request_analytic(
                analytic_other_company, self.main_company
            )
            self.StockRequestOrder.create(vals)

    @users("stock_request_user")
    def test_default_analytic(self):
        vals = self.prepare_order_request_analytic(self.analytic1, self.main_company)
        vals.update(
            {
                "default_analytic_distribution": {str(self.analytic1.id): 100.0},
            }
        )
        order = self.StockRequestOrder.create(vals)
        with Form(order) as order_form:
            with order_form.stock_request_ids.new() as line_form:
                line_form.product_id = self.product
                line_form.product_uom_qty = 5.0
        for line in order.stock_request_ids:
            self.assertEqual(
                line.analytic_distribution,
                {str(self.analytic1.id): 100.0},
                "La distribución analítica por defecto no se aplicó a la nueva línea.",
            )
