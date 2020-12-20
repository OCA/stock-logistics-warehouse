# Copyright 2020 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields
from odoo.exceptions import ValidationError

from odoo.addons.stock_request.tests.test_stock_request import TestStockRequest


class TestStockRequestPartner(TestStockRequest):
    def setUp(self):
        super(TestStockRequestPartner, self).setUp()
        self.partner = self.env.ref("base.res_partner_12")
        self.partner2 = self.env.ref("base.res_partner_2")

    def test_stock_request_partner_to_picking(self):
        vals = {
            "product_id": self.product.id,
            "product_uom_id": self.product.uom_id.id,
            "product_uom_qty": 5.0,
            "partner_id": self.partner.id,
        }
        request = (
            self.stock_request.with_user(self.stock_request_manager)
            .with_context(company_id=self.main_company.id)
            .create(vals)
        )
        self.product.route_ids = [(6, 0, self.route.ids)]
        request.with_user(self.stock_request_manager).action_confirm()
        self.assertEqual(request.picking_ids.partner_id, self.partner)

    def test_stock_request_order(self):
        expected_date = fields.Datetime.now()
        product2 = self._create_product("SH2", "Shoes 2", False)
        vals = {
            "partner_id": self.partner.id,
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": expected_date,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "partner_id": self.partner.id,
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "company_id": self.main_company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.warehouse.lot_stock_id.id,
                        "expected_date": expected_date,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "partner_id": self.partner.id,
                        "product_id": product2.id,
                        "product_uom_id": product2.uom_id.id,
                        "product_uom_qty": 10.0,
                        "company_id": self.main_company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.warehouse.lot_stock_id.id,
                        "expected_date": expected_date,
                    },
                ),
            ],
        }
        order = self.request_order.with_user(self.stock_request_user).create(vals)
        order.partner_id = self.partner2
        order._onchange_partner_id()
        self.assertEqual(order.stock_request_ids.partner_id, self.partner2)
        with self.assertRaises(ValidationError):
            order.stock_request_ids[0].partner_id = self.partner
        self.product.route_ids = [(6, 0, self.route.ids)]
        product2.route_ids = [(6, 0, self.route.ids)]
        order.with_user(self.stock_request_manager).action_confirm()
        self.assertEqual(len(order.picking_ids), 1)
