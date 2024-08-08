# Copyright 2024 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form

from odoo.addons.stock_request.tests.test_stock_request import TestStockRequest


class TestStockRequestBOM(TestStockRequest):
    def setUp(self):
        super().setUp()
        self.mrp_user_group = self.env.ref("mrp.group_mrp_user")
        self.stock_request_user.write({"groups_id": [(4, self.mrp_user_group.id)]})
        self.stock_request_manager.write({"groups_id": [(4, self.mrp_user_group.id)]})
        self.route_manufacture = self.warehouse.manufacture_pull_id.route_id
        self.product.write({"route_ids": [(6, 0, self.route_manufacture.ids)]})

        self.raw_1 = self._create_product("SL", "Sole", False)
        self.raw_2 = self._create_product("LC", "Lace", False)
        self.raw_3 = self._create_product("BT", "Button", False)

        self._update_qty_in_location(self.warehouse.lot_stock_id, self.raw_1, 10)
        self._update_qty_in_location(self.warehouse.lot_stock_id, self.raw_2, 10)
        self._update_qty_in_location(self.warehouse.lot_stock_id, self.raw_3, 10)

        self.bom = self._create_mrp_bom(self.product, [self.raw_1, self.raw_2])
        self.bom_raw_2 = self._create_mrp_bom(self.raw_2, [self.raw_3])

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

    def test_01_create_stock_request_with_bom(self):
        order_form = Form(self.request_order.with_user(self.stock_request_user))
        order_form.product_bom_id = self.product
        order_form.quantity_bom = 2
        order = order_form.save()
        self.assertEqual(len(order.stock_request_ids), 2)

        product_ids = order.stock_request_ids.mapped("product_id")
        expected_products = {self.raw_1.id, self.raw_3.id}
        actual_products = {product.id for product in product_ids}
        self.assertEqual(expected_products, actual_products)

    def test_02_update_quantity_bom(self):
        order_form = Form(self.request_order.with_user(self.stock_request_user))
        order_form.product_bom_id = self.product
        order_form.quantity_bom = 1
        order = order_form.save()
        for line in order.stock_request_ids:
            self.assertEqual(line.product_uom_qty, 1)

        order_form = Form(order)
        order_form.quantity_bom = 3
        order = order_form.save()
        for line in order.stock_request_ids:
            self.assertEqual(line.product_uom_qty, 3)

    def test_03_clear_product_bom(self):
        order_form = Form(self.request_order.with_user(self.stock_request_user))
        order_form.product_bom_id = self.product
        order_form.quantity_bom = 1
        order = order_form.save()
        self.assertEqual(len(order.stock_request_ids), 2)
        self.request_order.write({"product_bom_id": False})
        order_form = Form(order)
        order_form.product_bom_id = self.env["product.product"]
        order = order_form.save()
        self.assertEqual(len(order.stock_request_ids), 0)

    def test_04_invalid_quantity_bom(self):
        order_form = Form(self.request_order.with_user(self.stock_request_user))
        order_form.product_bom_id = self.product
        order_form.quantity_bom = -1

        with self.assertRaises(ValidationError):
            order_form.save()

    def test_05_product_without_bom(self):
        product_without_bom = self._create_product("PWB", "Product Without BOM", False)
        order_form = Form(self.request_order.with_user(self.stock_request_user))
        with self.assertRaises(UserError):
            order_form.product_bom_id = product_without_bom
