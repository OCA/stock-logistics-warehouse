# Copyright 2017-2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).
from odoo import fields

from odoo.addons.stock_request.tests import test_stock_request


class TestStockRequestSubmit(test_stock_request.TestStockRequest):
    def setUp(self):
        super().setUp()

    def test_stock_request_submit(self):
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

        order = self.request_order.with_user(self.stock_request_user).create(vals)

        stock_request = order.stock_request_ids

        self.product.route_ids = [(6, 0, self.route.ids)]
        order.action_submit()
        self.assertEqual(order.state, "submitted")
        self.assertEqual(stock_request.state, "submitted")
        order.action_confirm()
        self.assertEqual(order.state, "open")
        self.assertEqual(stock_request.state, "open")
