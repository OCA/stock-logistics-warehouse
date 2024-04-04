# Copyright 2017 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).


from odoo import fields

from odoo.addons.stock_request.tests.test_stock_request import TestStockRequest


class TestStockRequestBase(TestStockRequest):
    @classmethod
    def setUpClass(cls):
        super(TestStockRequestBase, cls).setUpClass()

    def test_onchange_direction_request(self):
        # Outbound direction
        vals = {
            "product_id": self.product.id,
            "product_uom_id": self.product.uom_id.id,
            "product_uom_qty": 5.0,
        }
        stock_request = (
            self.stock_request.with_user(self.stock_request_user)
            .with_context(company_id=self.main_company.id)
            .create(vals)
        )
        self.assertEqual(stock_request.location_id, self.warehouse.lot_stock_id)
        stock_request.direction = "outbound"
        stock_request._onchange_location_id()
        self.assertEqual(
            stock_request.location_id,
            stock_request.company_id.partner_id.property_stock_customer,
        )
        # Inbound direction
        vals = {
            "product_id": self.product.id,
            "product_uom_id": self.product.uom_id.id,
            "product_uom_qty": 5.0,
        }
        stock_request = (
            self.stock_request.with_user(self.stock_request_user)
            .with_context(company_id=self.main_company.id)
            .create(vals)
        )
        self.assertEqual(stock_request.location_id, self.warehouse.lot_stock_id)
        stock_request.direction = "inbound"
        stock_request._onchange_location_id()
        self.assertEqual(
            stock_request.location_id,
            stock_request.warehouse_id.lot_stock_id,
        )

    def test_onchange_direction_order(self):
        expected_date = fields.Datetime.now()
        # Outbound direction
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": expected_date,
            "direction": "outbound",
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
            self.request_order.with_user(self.stock_request_user)
            .with_context(company_id=self.main_company.id)
            .create(vals)
        )
        self.assertEqual(order.location_id, self.warehouse.lot_stock_id)
        order.direction = "outbound"
        order._onchange_location_id()
        order.onchange_location_id()
        self.assertEqual(
            order.stock_request_ids[:1].location_id,
            order.company_id.partner_id.property_stock_customer,
        )
        # Inbound direction
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": expected_date,
            "direction": "inbound",
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
            self.request_order.with_user(self.stock_request_user)
            .with_context(company_id=self.main_company.id)
            .create(vals)
        )
        self.assertEqual(order.location_id, self.warehouse.lot_stock_id)
        order.stock_request_ids[:1].route_id = self.route
        order.direction = "inbound"
        order._onchange_location_id()
        order.onchange_location_id()
        self.assertEqual(
            order.stock_request_ids[:1].location_id,
            order.warehouse_id.lot_stock_id,
        )
        self.assertFalse(order.stock_request_ids[:1].route_id)
