# Copyright 2017-2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestStockRequestAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Model
        cls.AccountAnalyticAccount = cls.env["account.analytic.account"]
        cls.AccountAnalyticTag = cls.env["account.analytic.tag"]
        cls.ProductProduct = cls.env["product.product"]
        cls.ResUsers = cls.env["res.users"]
        cls.StockRequest = cls.env["stock.request"]
        cls.StockRequestOrder = cls.env["stock.request.order"]
        cls.StockLocation = cls.env["stock.location"]
        cls.StockLocationRoute = cls.env["stock.location.route"]
        cls.StockRule = cls.env["stock.rule"]

        # Data
        cls.expected_date = fields.Datetime.now()
        cls.main_company = cls.env.ref("base.main_company")
        cls.company_2 = cls.env.ref("stock.res_company_1")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_request_user_group = cls.env.ref(
            "stock_request.group_stock_request_user"
        )
        cls.stock_request_manager_group = cls.env.ref(
            "stock_request.group_stock_request_manager"
        )
        cls.analytic1 = cls.AccountAnalyticAccount.create({"name": "Analytic"})
        cls.analytic2 = cls.AccountAnalyticAccount.create(
            {"name": "Analytic", "company_id": cls.company_2.id}
        )
        cls.analytic3 = cls.AccountAnalyticAccount.create({"name": "Analytic 3"})
        cls.demand_loc = cls.StockLocation.create(
            {
                "name": "demand_loc",
                "location_id": cls.warehouse.lot_stock_id.id,
                "usage": "internal",
            }
        )
        cls.demand_route = cls.StockLocationRoute.create(
            {
                "name": "Transfer",
                "product_categ_selectable": False,
                "product_selectable": True,
                "company_id": cls.main_company.id,
                "sequence": 10,
            }
        )
        cls.demand_rule = cls.StockRule.create(
            {
                "name": "Transfer",
                "route_id": cls.demand_route.id,
                "location_src_id": cls.warehouse.lot_stock_id.id,
                "location_id": cls.demand_loc.id,
                "action": "pull",
                "picking_type_id": cls.warehouse.int_type_id.id,
                "procure_method": "make_to_stock",
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.main_company.id,
            }
        )
        cls.product = cls.ProductProduct.create(
            {
                "name": "Test Product",
                "type": "product",
                "route_ids": [(6, 0, cls.demand_route.ids)],
            }
        )

    def prepare_order_request_analytic(self, analytic, company, analytic_tags=None):
        analytic_tags = analytic_tags or self.AccountAnalyticTag
        vals = {
            "company_id": company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.demand_loc.id,
            "expected_date": self.expected_date,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "analytic_account_id": analytic.id,
                        "analytic_tag_ids": [(4, tag.id) for tag in analytic_tags],
                        "company_id": company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.demand_loc.id,
                        "expected_date": self.expected_date,
                    },
                )
            ],
        }
        return vals

    def prepare_order_request_multi_analytic(self, analytic1, analytic2, company):
        vals = {
            "company_id": company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.demand_loc.id,
            "expected_date": self.expected_date,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "analytic_account_id": analytic1.id,
                        "company_id": company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.demand_loc.id,
                        "expected_date": self.expected_date,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "analytic_account_id": analytic2.id,
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
        analytic_tag = self.env.ref("analytic.tag_contract")
        vals = self.prepare_order_request_analytic(
            self.analytic1, self.main_company, analytic_tags=analytic_tag
        )
        order = self.StockRequestOrder.create(vals)
        req = order.stock_request_ids
        order.action_confirm()
        self.assertEqual(req.move_ids.mapped("analytic_account_id"), self.analytic1)
        self.assertEqual(req.move_ids.mapped("analytic_tag_ids"), analytic_tag)
        self.assertEqual(order.analytic_count, 1)
        action = order.with_context(
            analytic_type="analytic_account"
        ).action_view_analytic()
        self.assertTrue(action["res_id"], self.analytic1.id)
        action2 = self.analytic1.action_view_stock_request()
        self.assertTrue(action2["res_id"], order.id)

    def test_stock_multi_analytic(self):
        vals = self.prepare_order_request_multi_analytic(
            self.analytic1, self.analytic3, self.main_company
        )
        order = self.StockRequestOrder.create(vals)
        order.action_confirm()
        self.assertEqual(order.analytic_count, 2)

    def test_company(self):
        with self.assertRaises(UserError):
            vals = self.prepare_order_request_analytic(
                self.analytic2, self.main_company
            )
            self.StockRequestOrder.create(vals)

    def test_default_analytic(self):
        """
        Create request order with a default analytic
        """
        vals = self.prepare_order_request_analytic(
            self.AccountAnalyticAccount.browse(), self.main_company
        )
        vals.update(
            {
                "default_analytic_account_id": self.analytic1.id,
            }
        )
        order = self.StockRequestOrder.create(vals)
        with Form(order) as order_form:
            with order_form.stock_request_ids.new() as line_form:
                line_form.product_id = self.product
                line_form.product_uom_qty = 5.0
        self.assertEqual(
            order.default_analytic_account_id,
            order.stock_request_ids.mapped("analytic_account_id"),
        )
