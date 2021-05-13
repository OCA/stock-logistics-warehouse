# Copyright 2017-2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields

from odoo.addons.stock_request.tests import test_stock_request

from ..hooks import uninstall_hook


class TestStockRequestSubmit(test_stock_request.TestStockRequest):
    def setUp(self):
        super().setUp()
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
        self.order = self.request_order.with_user(self.stock_request_user).create(vals)
        self.stock_request = self.order.stock_request_ids

    def test_stock_request_submit(self):
        self.product.route_ids = [(6, 0, self.route.ids)]
        self.order.action_submit()
        self.assertEqual(self.order.state, "submitted")
        self.assertEqual(self.stock_request.state, "submitted")
        self.order.action_confirm()
        self.assertEqual(self.order.state, "open")
        self.assertEqual(self.stock_request.state, "open")

    def test_uninstall_hook(self):
        # Check state before uninstall
        self.product.route_ids = [(6, 0, self.route.ids)]
        self.order.action_submit()
        self.assertEqual(self.order.state, "submitted")
        self.assertEqual(self.stock_request.state, "submitted")

        # Uninstall this module
        uninstall_hook(self.cr, self.registry)

        # Check state after uninstall
        self.assertEqual(self.order.state, "draft")
        self.assertEqual(self.stock_request.state, "draft")
