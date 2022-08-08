# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo import fields


class TestStockOrderpointProcureLocation(common.TransactionCase):
    def setUp(self):
        super(TestStockOrderpointProcureLocation, self).setUp()

        # Get required Model
        productObj = self.env["product.product"]
        self.purchase_model = self.env["purchase.order"]
        self.purchase_line_model = self.env["purchase.order.line"]
        self.warehouse = self.env.ref("stock.warehouse0")
        self.warehouse.reception_steps = "two_steps"
        self.location_stock = self.env.ref("stock.stock_location_stock")
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.location_input = self.env.ref("stock.stock_location_company")

        self.productA = productObj.create(
            {
                "name": "product A",
                "standard_price": 1,
                "type": "product",
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
                "default_code": "A",
                "route_ids": [
                    (6, 0, [self.env.ref("purchase_stock.route_warehouse0_buy").id])
                ],
                "variant_seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.env.ref("base.res_partner_3").id,
                            "delay": 3,
                            "min_qty": 1,
                            "price": 72,
                        },
                    )
                ],
            }
        )

        self.productB = productObj.create(
            {
                "name": "product B",
                "standard_price": 1,
                "type": "product",
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
                "default_code": "B",
                "variant_seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.env.ref("base.res_partner_3").id,
                            "delay": 3,
                            "min_qty": 1,
                            "price": 72,
                        },
                    )
                ],
            }
        )

        self.productC = productObj.create(
            {
                "name": "product C",
                "standard_price": 1,
                "type": "product",
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
                "default_code": "C",
                "variant_seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.env.ref("base.res_partner_3").id,
                            "delay": 5,
                            "min_qty": 1,
                            "price": 10,
                        },
                    )
                ],
            }
        )

    def _create_purchase(self, line_products):
        """Create a purchase order.

        ``line_products`` is a list of tuple [(product, qty, orderpoint)]
        """
        lines = []
        for product, qty, orderpoint in line_products:
            line_values = {
                "name": product.name,
                "product_id": product.id,
                "product_qty": qty,
                "orderpoint_id": orderpoint.id,
                "product_uom": product.uom_id.id,
                "price_unit": 500,
                "date_planned": fields.datetime.now(),
            }
            lines.append((0, 0, line_values))
        return self.purchase_model.create(
            {"partner_id": self.env.ref("base.res_partner_3").id, "order_line": lines}
        )

    def test_01_stock_orderpoint_procure_location(self):
        """
        Test the destination location is correct
        """
        self.env["stock.warehouse.orderpoint"].create(
            {
                "warehouse_id": self.warehouse.id,
                "location_id": self.location_stock.id,
                "product_id": self.productA.id,
                "product_max_qty": 24,
                "product_min_qty": 12,
                "product_uom": self.uom_unit.id,
                "procure_location_id": self.location_input.id,
            }
        )

        purchase_line = self.purchase_line_model.search(
            [("product_id", "=", self.productA.id)]
        )
        self.assertEqual(len(purchase_line), 0)

        self.env["procurement.group"].run_scheduler()
        # As per route configuration, it will create Purchase order
        purchase_line = self.purchase_line_model.search(
            [("product_id", "=", self.productA.id)]
        )
        self.assertEqual(len(purchase_line), 1)
        self.assertEqual(purchase_line.product_qty, 24)
        purchase_line.order_id.button_confirm()
        self.assertEqual(
            purchase_line.order_id.picking_ids[0].move_lines[0].location_dest_id.id,
            self.location_input.id,
            purchase_line.order_id.picking_ids[0].move_lines[0].location_dest_id.name,
        )

    def test_02_considering_open_po(self):
        """
        Test we consider confirmed POs received in procure location
        """

        self.env["stock.warehouse.orderpoint"].create(
            {
                "warehouse_id": self.warehouse.id,
                "location_id": self.location_stock.id,
                "product_id": self.productB.id,
                "product_max_qty": 35,
                "product_min_qty": 20,
                "product_uom": self.uom_unit.id,
                "procure_location_id": self.location_input.id,
            }
        )
        purchase_line = self.purchase_line_model.search(
            [("product_id", "=", self.productB.id)]
        )
        self.assertEqual(len(purchase_line), 0)
        # The scheduler should create demand for the extra
        self.env["procurement.group"].run_scheduler()
        # As per route configuration, it will create Purchase order
        purchase_line = self.purchase_line_model.search(
            [("product_id", "=", self.productB.id)]
        )
        self.assertEqual(sum(purchase_line.mapped("product_qty")), 35)
