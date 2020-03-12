# Copyright 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields
from odoo.tests import Form, common


class TestStockRequestMrp(common.TransactionCase):
    def setUp(self):
        super().setUp()

        # common models
        self.stock_request = self.env["stock.request"]
        self.produce_wiz = self.env["mrp.product.produce"]

        # refs
        self.stock_request_user_group = self.env.ref(
            "stock_request.group_stock_request_user"
        )
        self.stock_request_manager_group = self.env.ref(
            "stock_request.group_stock_request_manager"
        )
        self.mrp_user_group = self.env.ref("mrp.group_mrp_user")
        self.main_company = self.env.ref("base.main_company")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.categ_unit = self.env.ref("uom.product_uom_categ_unit")

        # common data
        self.company_2 = self.env["res.company"].create({"name": "Comp2"})
        self.wh2 = self.env["stock.warehouse"].search(
            [("company_id", "=", self.company_2.id)], limit=1
        )
        self.stock_request_user = self._create_user(
            "stock_request_user",
            [self.stock_request_user_group.id, self.mrp_user_group.id],
            [self.main_company.id, self.company_2.id],
        )
        self.stock_request_manager = self._create_user(
            "stock_request_manager",
            [self.stock_request_manager_group.id, self.mrp_user_group.id],
            [self.main_company.id, self.company_2.id],
        )
        self.route_manufacture = self.warehouse.manufacture_pull_id.route_id
        self.product = self._create_product(
            "SH", "Shoes", False, self.route_manufacture.ids
        )

        self.raw_1 = self._create_product("SL", "Sole", False, [])
        self._update_qty_in_location(self.warehouse.lot_stock_id, self.raw_1, 10)
        self.raw_2 = self._create_product("LC", "Lace", False, [])
        self._update_qty_in_location(self.warehouse.lot_stock_id, self.raw_2, 10)

        self.bom = self._create_mrp_bom(self.product, [self.raw_1, self.raw_2])

        self.uom_pair = self.env["uom.uom"].create(
            {
                "name": "Test-Pair",
                "category_id": self.categ_unit.id,
                "factor_inv": 2,
                "uom_type": "bigger",
                "rounding": 0.001,
            }
        )

    def _update_qty_in_location(self, location, product, quantity):
        self.env["stock.quant"]._update_available_quantity(product, location, quantity)

    def _create_user(self, name, group_ids, company_ids):
        return (
            self.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": name,
                    "password": "demo",
                    "login": name,
                    "email": str(name) + "@test.com",
                    "groups_id": [(6, 0, group_ids)],
                    "company_ids": [(6, 0, company_ids)],
                }
            )
        )

    def _create_product(self, default_code, name, company_id, route_ids):
        return self.env["product.product"].create(
            {
                "name": name,
                "default_code": default_code,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "company_id": company_id,
                "type": "product",
                "route_ids": [(6, 0, route_ids)],
            }
        )

    def _create_mrp_bom(self, product_id, raw_materials):
        bom = self.env["mrp.bom"].create(
            {
                "product_id": product_id.id,
                "product_tmpl_id": product_id.product_tmpl_id.id,
                "product_uom_id": product_id.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        for raw_mat in raw_materials:
            self.env["mrp.bom.line"].create(
                {"bom_id": bom.id, "product_id": raw_mat.id, "product_qty": 1}
            )

        return bom

    def _produce(self, mo, qty=0.0):
        wiz = Form(
            self.produce_wiz.with_context({"active_id": mo.id, "active_ids": [mo.id]})
        )
        wiz.qty_producing = qty or mo.product_qty
        produce_wizard = wiz.save()
        produce_wizard.do_produce()
        return True

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

        self.assertEqual(len(order.production_ids), 1)
        self.assertEqual(len(order.stock_request_ids.production_ids), 1)
        self.assertEqual(order.stock_request_ids.qty_in_progress, 5.0)

        manufacturing_order = order.production_ids[0]
        self.assertEqual(
            manufacturing_order.company_id, order.stock_request_ids[0].company_id
        )

        self._produce(manufacturing_order, 5.0)
        self.assertEqual(order.stock_request_ids.qty_in_progress, 5.0)
        self.assertEqual(order.stock_request_ids.qty_done, 0.0)

        manufacturing_order.button_mark_done()
        self.assertEqual(order.stock_request_ids.qty_in_progress, 0.0)
        self.assertEqual(order.stock_request_ids.qty_done, 5.0)

    def test_view_actions(self):
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

        order = self.env["stock.request.order"].create(vals)

        order.action_confirm()

        stock_request = order.stock_request_ids

        action = stock_request.action_view_mrp_production()

        self.assertEqual("views" in action.keys(), True)
        self.assertEqual(action["res_id"], stock_request.production_ids[0].id)

        action = stock_request.production_ids[0].action_view_stock_request()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_id"], stock_request.id)

        action = order.action_view_mrp_production()

        self.assertEqual("views" in action.keys(), True)
        self.assertEqual(action["res_id"], order.production_ids[0].id)
