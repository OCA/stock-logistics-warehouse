# Copyright 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2022 Tecnativa - Pedro M. Baeza
# Copyright 2022 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields
from odoo.tests import Form

from odoo.addons.stock_request.tests.test_stock_request import TestStockRequest


class TestStockRequestMrp(TestStockRequest):
    def setUp(self):
        super().setUp()
        self.mrp_user_group = self.env.ref("mrp.group_mrp_user")
        # common data
        self.stock_request_user.write({"groups_id": [(4, self.mrp_user_group.id)]})
        self.stock_request_manager.write({"groups_id": [(4, self.mrp_user_group.id)]})
        self.route_manufacture = self.warehouse.manufacture_pull_id.route_id
        self.product.write({"route_ids": [(6, 0, self.route_manufacture.ids)]})
        self.raw_1 = self._create_product("SL", "Sole", False)
        self._update_qty_in_location(self.warehouse.lot_stock_id, self.raw_1, 10)
        self.raw_2 = self._create_product("LC", "Lace", False)
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
        mo_form = Form(mo)
        mo_form.qty_producing = qty
        mo_form.save()

    def _create_stock_request(self, user, products):
        order_form = Form(
            self.request_order.with_user(user).with_context(
                default_company_id=self.main_company.id,
                default_warehouse_id=self.warehouse.id,
                default_location_id=self.warehouse.lot_stock_id,
            )
        )
        order_form.expected_date = fields.Datetime.now()
        for product_data in products:
            with order_form.stock_request_ids.new() as item_form:
                item_form.product_id = product_data[0]
                item_form.product_uom_qty = product_data[1]
        return order_form.save()

    def test_create_request_01(self):
        """Single Stock request with buy rule"""
        order = self._create_stock_request(self.stock_request_user, [(self.product, 5)])
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
        manufacturing_order.action_confirm()
        manufacturing_order.write(
            {"qty_producing": manufacturing_order.product_uom_qty}
        )
        manufacturing_order._set_qty_producing()

        manufacturing_order.with_context(skip_immediate=True).button_mark_done()
        self.assertEqual(order.stock_request_ids.qty_in_progress, 0.0)
        self.assertEqual(order.stock_request_ids.qty_done, 5.0)
        order2 = order.copy()
        self.assertFalse(order2.production_ids)

    def test_stock_request_order_action_cancel(self):
        order = self._create_stock_request(self.stock_request_user, [(self.product, 5)])
        order.action_confirm()
        production = fields.first(order.stock_request_ids.production_ids)
        self.assertEqual(production.state, "confirmed")
        order.with_context(bypass_confirm_wizard=True).action_cancel()
        self.assertEqual(production.state, "cancel")

    def test_stock_request_order_production_action_cancel(self):
        order = self._create_stock_request(self.stock_request_user, [(self.product, 5)])
        order.action_confirm()
        production = fields.first(order.stock_request_ids.production_ids)
        self.assertEqual(production.state, "confirmed")
        production.action_cancel()
        self.assertEqual(order.state, "cancel")

    def test_view_actions(self):
        order = self._create_stock_request(self.stock_request_user, [(self.product, 5)])
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
