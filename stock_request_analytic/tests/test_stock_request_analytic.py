# Copyright 2017-2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import Form

from odoo.addons.stock_request.tests import test_stock_request


class TestStockRequestAnalytic(test_stock_request.TestStockRequest):
    def setUp(self):
        super(TestStockRequestAnalytic, self).setUp()
        self.analytic_model = self.env["account.analytic.account"]
        self.analytic = self.analytic_model.create({"name": "Pizza"})
        self.analytic2 = self.analytic_model.create(
            {"name": "Pizza", "company_id": self.company_2.id}
        )
        self.analytic3 = self.analytic_model.create({"name": "Hamburger"})
        self.demand_loc = self.env["stock.location"].create(
            {
                "name": "demand_loc",
                "location_id": self.warehouse.lot_stock_id.id,
                "usage": "internal",
            }
        )
        self.demand_route = self.env["stock.location.route"].create(
            {
                "name": "Transfer",
                "product_categ_selectable": False,
                "product_selectable": True,
                "company_id": self.main_company.id,
                "sequence": 10,
            }
        )
        self.pizza = self._create_product("PZ", "Pizza", False)
        self.demand_rule = self.env["stock.rule"].create(
            {
                "name": "Transfer",
                "route_id": self.demand_route.id,
                "location_src_id": self.warehouse.lot_stock_id.id,
                "location_id": self.demand_loc.id,
                "action": "pull",
                "picking_type_id": self.warehouse.int_type_id.id,
                "procure_method": "make_to_stock",
                "warehouse_id": self.warehouse.id,
                "company_id": self.main_company.id,
            }
        )
        self.pizza.route_ids = [(6, 0, self.demand_route.ids)]

    def prepare_order_request_analytic(self, analytic, company, analytic_tags=None):
        expected_date = fields.Datetime.now()
        analytic_tags = analytic_tags or self.env["account.analytic.tag"]
        vals = {
            "company_id": company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.demand_loc.id,
            "expected_date": expected_date,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.pizza.id,
                        "product_uom_id": self.pizza.uom_id.id,
                        "product_uom_qty": 5.0,
                        "analytic_account_id": analytic.id,
                        "analytic_tag_ids": [(4, tag.id) for tag in analytic_tags],
                        "company_id": company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.demand_loc.id,
                        "expected_date": expected_date,
                    },
                )
            ],
        }
        return vals

    def prepare_order_request_multi_analytic(self, analytic1, analytic2, company):
        expected_date = fields.Datetime.now()
        vals = {
            "company_id": company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.demand_loc.id,
            "expected_date": expected_date,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.pizza.id,
                        "product_uom_id": self.pizza.uom_id.id,
                        "product_uom_qty": 5.0,
                        "analytic_account_id": analytic1.id,
                        "company_id": company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.demand_loc.id,
                        "expected_date": expected_date,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": self.pizza.id,
                        "product_uom_id": self.pizza.uom_id.id,
                        "product_uom_qty": 5.0,
                        "analytic_account_id": analytic2.id,
                        "company_id": company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.demand_loc.id,
                        "expected_date": expected_date,
                    },
                ),
            ],
        }
        return vals

    def test_stock_analytic(self):
        analytic_tag = self.env.ref("analytic.tag_contract")
        vals = self.prepare_order_request_analytic(
            self.analytic, self.main_company, analytic_tags=analytic_tag
        )
        order = self.env["stock.request.order"].create(vals)
        req = order.stock_request_ids
        order.action_confirm()
        self.assertEqual(req.move_ids.mapped("analytic_account_id"), self.analytic)
        self.assertEqual(req.move_ids.mapped("analytic_tag_ids"), analytic_tag)
        self.assertEqual(order.analytic_count, 1)
        action = order.with_context(
            analytic_type="analytic_account"
        ).action_view_analytic()
        self.assertTrue(action["res_id"], self.analytic.id)
        action2 = self.analytic.action_view_stock_request()
        self.assertTrue(action2["res_id"], order.id)

    def test_stock_multi_analytic(self):
        vals = self.prepare_order_request_multi_analytic(
            self.analytic, self.analytic3, self.main_company
        )
        order = self.env["stock.request.order"].create(vals)
        order.action_confirm()
        self.assertEqual(order.analytic_count, 2)

    def test_company(self):
        with self.assertRaises(UserError):
            vals = self.prepare_order_request_analytic(
                self.analytic2, self.main_company
            )
            self.env["stock.request.order"].create(vals)

    def test_default_analytic(self):
        """
        Create request order with a default analytic
        """
        vals = self.prepare_order_request_analytic(
            self.analytic_model.browse(), self.main_company
        )
        vals.update(
            {
                "default_analytic_account_id": self.analytic.id,
            }
        )
        order = self.env["stock.request.order"].create(vals)
        with Form(order) as order_form:
            with order_form.stock_request_ids.new() as line_form:
                line_form.product_id = self.pizza
                line_form.product_uom_qty = 5.0
        self.assertEqual(
            order.default_analytic_account_id,
            order.stock_request_ids.mapped("analytic_account_id"),
        )
