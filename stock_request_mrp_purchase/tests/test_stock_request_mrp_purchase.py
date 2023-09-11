# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields
from odoo.tests import Form

from odoo.addons.stock_request.tests.test_stock_request import TestStockRequest


class TestStockRequestMrpPurchase(TestStockRequest):
    def setUp(self):
        super().setUp()
        self.mrp_user_group = self.env.ref("mrp.group_mrp_user")
        # common data
        self.stock_request_user.write({"groups_id": [(4, self.mrp_user_group.id)]})
        self.route_manufacture = self.warehouse.manufacture_pull_id.route_id
        self.mto_route = self.env.ref("stock.route_warehouse0_mto")
        self.mto_route.active = True
        self.product.write(
            {"route_ids": [(6, 0, [self.route_manufacture.id, self.mto_route.id])]}
        )
        self.raw_1 = self._create_product("SL", "Sole", False)
        self.raw_1.write(
            {"route_ids": [(6, 0, [self.route_manufacture.id, self.mto_route.id])]}
        )
        self._create_mrp_bom(self.product, [self.raw_1])
        self.raw_1_component = self._create_product("SLA", "Sole Component", False)
        self._create_mrp_bom(self.raw_1, [self.raw_1_component])
        self.buy_route = self.env.ref("purchase_stock.route_warehouse0_buy")
        self.supplier = self.env["res.partner"].create({"name": "Mr Odoo"})
        self.raw_1_component.write(
            {
                "seller_ids": [(0, 0, {"name": self.supplier.id})],
                "route_ids": [(6, 0, [self.buy_route.id, self.mto_route.id])],
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

    def _create_stock_request_only(self, user, product_data):
        request_form = Form(
            self.stock_request.with_user(user).with_context(
                default_company_id=self.main_company.id,
                default_warehouse_id=self.warehouse.id,
                default_location_id=self.warehouse.lot_stock_id,
            )
        )
        request_form.expected_date = fields.Date.today()
        request_form.product_id = product_data[0]
        request_form.product_uom_qty = product_data[1]
        return request_form.save()

    def test_stock_request_order_exception(self):
        order = self._create_stock_request(self.stock_request_user, [(self.product, 5)])
        order.action_confirm()
        children = order.production_ids._get_children()
        res = children.action_view_purchase_orders()
        purchase = self.env[res["res_model"]].browse(res["res_id"])
        purchase.button_cancel()
        self.assertIn(
            self.env.ref("mail.mail_activity_data_warning"),
            order.activity_ids.mapped("activity_type_id"),
        )

    def test_stock_request_exception(self):
        request = self._create_stock_request_only(
            self.stock_request_user, (self.product, 5)
        )
        request.action_confirm()
        children = request.production_ids._get_children()
        res = children.action_view_purchase_orders()
        purchase = self.env[res["res_model"]].browse(res["res_id"])
        purchase.button_cancel()
        self.assertIn(
            self.env.ref("mail.mail_activity_data_warning"),
            request.activity_ids.mapped("activity_type_id"),
        )
