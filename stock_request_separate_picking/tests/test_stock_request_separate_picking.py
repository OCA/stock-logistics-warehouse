# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.stock_request.tests import test_stock_request


class TestStockRequestSeparatePicking(test_stock_request.TestStockRequest):
    def setUp(self):
        super().setUp()
        self.expected_date = fields.Datetime.now()
        self.main_company.stock_request_allow_separate_picking = True

    def test_create_stock_request(self):
        vals = {
            "product_id": self.product.id,
            "product_uom_id": self.product.uom_id.id,
            "product_uom_qty": 5.0,
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": self.expected_date,
        }
        self.product.route_ids = [(6, 0, self.route.ids)]
        # Create stock requests
        stock_request_1 = self.stock_request.with_user(self.stock_request_user).create(
            vals
        )
        stock_request_2 = self.stock_request.with_user(self.stock_request_user).create(
            vals
        )
        self.assertEqual(stock_request_1.state, "draft")
        self.assertEqual(len(stock_request_1.picking_ids), 0)
        self.assertEqual(stock_request_2.state, "draft")
        self.assertEqual(len(stock_request_2.picking_ids), 0)
        # Confirm stock requests
        stock_request_1.with_user(self.stock_request_manager).action_confirm()
        stock_request_2.with_user(self.stock_request_manager).action_confirm()
        self.assertEqual(stock_request_1.state, "open")
        self.assertEqual(len(stock_request_1.picking_ids), 1)
        self.assertEqual(stock_request_2.state, "open")
        self.assertEqual(len(stock_request_2.picking_ids), 1)
        self.assertNotEqual(stock_request_1.picking_ids, stock_request_2.picking_ids)

    def test_create_stock_request_order(self):
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": self.expected_date,
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
                        "expected_date": self.expected_date,
                    },
                )
            ],
        }
        self.product.route_ids = [(6, 0, self.route.ids)]
        # Create stock request order
        stock_request_order_1 = self.request_order.with_user(
            self.stock_request_user
        ).create(vals)
        stock_request_order_2 = self.request_order.with_user(
            self.stock_request_user
        ).create(vals)
        self.assertEqual(stock_request_order_1.state, "draft")
        self.assertEqual(len(stock_request_order_1.picking_ids), 0)
        self.assertEqual(stock_request_order_2.state, "draft")
        self.assertEqual(len(stock_request_order_2.picking_ids), 0)
        # Confirm stock requests
        stock_request_order_1.with_user(self.stock_request_manager).action_confirm()
        stock_request_order_2.with_user(self.stock_request_manager).action_confirm()
        self.assertEqual(stock_request_order_1.state, "open")
        self.assertEqual(len(stock_request_order_1.picking_ids), 1)
        self.assertEqual(stock_request_order_2.state, "open")
        self.assertEqual(len(stock_request_order_2.picking_ids), 1)
        self.assertNotEqual(
            stock_request_order_1.picking_ids, stock_request_order_2.picking_ids
        )
