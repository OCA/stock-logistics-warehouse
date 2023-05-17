# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import Form, common


class TestStockRequestPurchaseMrp(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.route_mto = cls.env.ref("stock.route_warehouse0_mto")
        cls.route_mto.active = True
        cls.route_manufacture = cls.env.ref("mrp.route_warehouse0_manufacture")
        cls.route_buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.supplier_a = cls.env["res.partner"].create({"name": "Test supplier A"})
        cls.supplier_b = cls.env["res.partner"].create({"name": "Test supplier B"})
        cls.component_a = cls.env["product.product"].create(
            {
                "name": "Test component A",
                "type": "product",
                "route_ids": [(6, 0, [cls.route_buy.id, cls.route_mto.id])],
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.supplier_a.id,
                            "min_qty": 1,
                            "price": 10,
                        },
                    )
                ],
            }
        )
        cls.component_b = cls.env["product.product"].create(
            {
                "name": "Test component B",
                "type": "product",
                "route_ids": [(6, 0, [cls.route_buy.id, cls.route_mto.id])],
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.supplier_b.id,
                            "min_qty": 1,
                            "price": 10,
                        },
                    )
                ],
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "product",
                "route_ids": [(6, 0, [cls.route_manufacture.id])],
            }
        )
        cls.bom = cls._create_mrp_bom(cls)

    def _create_mrp_bom(self):
        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_tmpl_id = self.product.product_tmpl_id
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = self.component_a
            line_form.product_qty = 1
        with mrp_bom_form.bom_line_ids.new() as line_form:
            line_form.product_id = self.component_b
            line_form.product_qty = 1
        return mrp_bom_form.save()

    def test_stock_request_order(self):
        stock_request = self.env["stock.request"].create(
            {
                "product_id": self.product.id,
                "expected_date": fields.datetime.today(),
                "product_uom_id": self.product.uom_id.id,
                "product_uom_qty": 1,
                "route_id": self.route_manufacture.id,
            }
        )
        stock_request.action_confirm()
        self.assertEqual(stock_request.state, "open")
        self.assertEqual(stock_request.purchase_count, 2)
        res = stock_request.production_ids.action_view_purchase_orders()
        purchases = self.env[res["res_model"]].search(res["domain"])
        purchase_a = purchases.filtered(lambda x: x.partner_id == self.supplier_a)
        purchase_b = purchases.filtered(lambda x: x.partner_id == self.supplier_a)
        self.assertIn(purchase_a, stock_request.purchase_ids)
        self.assertIn(purchase_b, stock_request.purchase_ids)
