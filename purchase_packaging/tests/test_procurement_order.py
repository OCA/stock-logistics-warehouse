# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta

import odoo.tests.common as common
from odoo import fields


class TestProcurementOrder(common.TransactionCase):
    def setUp(self):
        """ Create a packagings with uom  product_uom_dozen on
                * product_product_3 (uom is product_uom_unit)
        """
        super().setUp()
        product_obj = self.env["product.product"]
        # Create new product
        vals = {
            "name": "Product Purchase Pack Test",
            "categ_id": self.env.ref("product.product_category_5").id,
            "list_price": 30.0,
            "standard_price": 20.0,
            "type": "product",
            "uom_id": self.env.ref("uom.product_uom_unit").id,
        }
        self.product_test = product_obj.create(vals)
        self.product_packaging_3 = self.env["product.packaging"].create(
            {
                "product_id": self.product_test.id,
                "uom_id": self.env.ref("uom.product_uom_dozen").id,
                "name": "Packaging Dozen",
            }
        )
        self.sp_30 = self.env.ref("product.product_supplierinfo_1")
        self.sp_30.product_tmpl_id = self.product_test.product_tmpl_id
        self.sp_30.currency_id = self.env.user.company_id.currency_id
        self.sp_30.date_start = fields.Datetime.from_string(
            fields.Datetime.now()
        ) - timedelta(days=10)
        self.product_uom_8 = self.env["uom.uom"].create(
            {
                "category_id": self.env.ref("uom.product_uom_categ_unit").id,
                "name": "COL8",
                "factor_inv": 8,
                "uom_type": "bigger",
                "rounding": 1.0,
            }
        )
        self.env["purchase.order"].search([("state", "=", "draft")]).button_cancel()

    def test_procurement(self):
        # On supplierinfo set price to 3
        # On supplierinfo set min_qty as 0
        # Create procurement line with rule buy and quantity 17
        # run procurement
        self.product_test.route_ids = [
            (4, self.env.ref("purchase_stock.route_warehouse0_buy").id)
        ]
        self.env.ref("uom.product_uom_unit").rounding = 1

        self.sp_30.min_qty = 0
        self.sp_30.price = 3
        existing_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product_test.id)], order="id"
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_test,
                    17,
                    self.env.ref("uom.product_uom_unit"),
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        new_po_lines = self.env["purchase.order.line"].search(
            [
                ("product_id", "=", self.product_test.id),
                ("id", "not in", existing_po_lines.ids),
            ],
            order="id",
        )

        # Check product_purchase_uom_id is product_uom_unit
        # Check product_purchase_qty is 17
        # Check product_qty is 17
        # Check packaging_id is False
        # Check product_uom is product_uom_unit
        # Check price_unit is 3
        self.assertEqual(len(new_po_lines), 1)
        self.assertEqual(
            self.env.ref("uom.product_uom_unit"), new_po_lines.product_purchase_uom_id,
        )
        self.assertEqual(17, new_po_lines.product_purchase_qty)
        self.assertEqual(17, new_po_lines.product_qty)
        self.assertFalse(new_po_lines.packaging_id)
        self.assertEqual(
            self.env.ref("uom.product_uom_unit"), new_po_lines.product_uom,
        )
        self.assertEqual(3, new_po_lines.price_unit)
        #  Confirm Purchase Order to avoid group
        new_po_lines.order_id.button_confirm()

        # Create procurement line with rule buy and quantity 1 dozen
        # run procurement
        existing_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product_test.id)], order="id"
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_test,
                    1,
                    self.env.ref("uom.product_uom_dozen"),
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        new_po_lines = self.env["purchase.order.line"].search(
            [
                ("product_id", "=", self.product_test.id),
                ("id", "not in", existing_po_lines.ids),
            ],
            order="id",
        )
        # Check product_purchase_uom_id is product_uom_unit
        # Check product_purchase_qty is 12
        # Check product_qty is 12
        # Check packaging_id is False
        # Check product_uom is product_uom_unit
        # Check price_unit is 3
        self.assertEqual(len(new_po_lines), 1)
        self.assertEqual(
            self.env.ref("uom.product_uom_unit"), new_po_lines.product_purchase_uom_id,
        )
        self.assertEqual(12, new_po_lines.product_purchase_qty)
        self.assertEqual(12, new_po_lines.product_qty)
        self.assertFalse(new_po_lines.packaging_id)
        self.assertEqual(
            self.env.ref("uom.product_uom_unit"), new_po_lines.product_uom,
        )
        self.assertEqual(3, new_po_lines.price_unit)
        # Confirm Purchase Order to avoid group
        new_po_lines.order_id.button_confirm()

        # On supplierinfo set product_uom_8 as min_qty_uom_id
        # Create procurement line with rule buy and quantity 17
        # run procurement
        self.sp_30.min_qty_uom_id = self.product_uom_8

        existing_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product_test.id)], order="id"
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_test,
                    17,
                    self.env.ref("uom.product_uom_unit"),
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        new_po_lines = self.env["purchase.order.line"].search(
            [
                ("product_id", "=", self.product_test.id),
                ("id", "not in", existing_po_lines.ids),
            ],
            order="id",
        )

        # Check product_purchase_uom_id is product_uom_8
        # Check product_purchase_qty is 3
        # Check product_qty is 8*3 = 24
        # Check packaging_id is False
        # Check product_uom is product_uom_unit
        # Check price_unit is 3
        self.assertEqual(len(new_po_lines), 1)
        self.assertEqual(self.product_uom_8, new_po_lines.product_purchase_uom_id)
        self.assertEqual(3, new_po_lines.product_purchase_qty)
        self.assertEqual(24, new_po_lines.product_qty)
        self.assertFalse(new_po_lines.packaging_id)
        self.assertEqual(
            self.env.ref("uom.product_uom_unit"), new_po_lines.product_uom,
        )
        self.assertEqual(3, new_po_lines.price_unit)
        # Confirm Purchase Order to avoid group
        new_po_lines.order_id.button_confirm()

        # Create procurement line with rule buy and quantity 1 dozen
        # run procurement
        existing_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product_test.id)], order="id"
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_test,
                    1,
                    self.env.ref("uom.product_uom_dozen"),
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        new_po_lines = self.env["purchase.order.line"].search(
            [
                ("product_id", "=", self.product_test.id),
                ("id", "not in", existing_po_lines.ids),
            ],
            order="id",
        )
        # Check product_purchase_uom_id is product_uom_8
        # Check product_purchase_qty is 2
        # Check product_qty is 8*2 = 16
        # Check packaging_id is False
        # Check product_uom is product_uom_unit
        # Check price_unit is 3
        self.assertEqual(self.product_uom_8, new_po_lines.product_purchase_uom_id)
        self.assertEqual(2, new_po_lines.product_purchase_qty)
        self.assertEqual(16, new_po_lines.product_qty)
        self.assertFalse(new_po_lines.packaging_id)
        self.assertEqual(
            self.env.ref("uom.product_uom_unit"), new_po_lines.product_uom,
        )
        self.assertEqual(3, new_po_lines.price_unit)
        # Confirm Purchase Order to avoid group
        new_po_lines.order_id.button_confirm()

        # On supplierinfo set packaging product_packaging_3 (dozen)
        # Create procurement line with rule buy and quantity 17
        # run procurement
        self.sp_30.packaging_id = self.product_packaging_3

        existing_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product_test.id)], order="id"
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_test,
                    17,
                    self.env.ref("uom.product_uom_unit"),
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        new_po_lines = self.env["purchase.order.line"].search(
            [
                ("product_id", "=", self.product_test.id),
                ("id", "not in", existing_po_lines.ids),
            ],
            order="id",
        )

        # Check product_purchase_uom_id is product_uom_8
        # Check product_purchase_qty is 1
        # Check product_qty is 8*1 = 8
        # Check packaging_id is product_packaging_3
        # Check product_uom is product_uom_dozen
        # Check price_unit is 3*12 = 36
        self.assertEqual(self.product_uom_8, new_po_lines.product_purchase_uom_id)
        self.assertEqual(1, new_po_lines.product_purchase_qty)
        self.assertEqual(8, new_po_lines.product_qty)
        self.assertEqual(self.product_packaging_3, new_po_lines.packaging_id)
        self.assertEqual(
            self.env.ref("uom.product_uom_dozen"), new_po_lines.product_uom,
        )
        self.assertEqual(3, new_po_lines.price_unit)
        # Confirm Purchase Order to avoid group
        new_po_lines.order_id.button_confirm()

        # Create procurement line with rule buy and quantity 1 dozen
        # run procurement
        existing_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product_test.id)], order="id"
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_test,
                    1,
                    self.env.ref("uom.product_uom_dozen"),
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        new_po_lines = self.env["purchase.order.line"].search(
            [
                ("product_id", "=", self.product_test.id),
                ("id", "not in", existing_po_lines.ids),
            ],
            order="id",
        )
        # Check product_purchase_uom_id is product_uom_8
        # Check product_purchase_qty is 1
        # Check product_qty is 8*1 = 8
        # Check packaging_id is product_packaging_3
        # Check product_uom is product_uom_dozen
        self.assertEqual(self.product_uom_8, new_po_lines.product_purchase_uom_id)
        self.assertEqual(1, new_po_lines.product_purchase_qty)
        self.assertEqual(8, new_po_lines.product_qty)
        self.assertEqual(self.product_packaging_3, new_po_lines.packaging_id)
        self.assertEqual(
            self.env.ref("uom.product_uom_dozen"), new_po_lines.product_uom,
        )
        self.assertEqual(3, new_po_lines.price_unit)
        # Confirm Purchase Order to avoid group
        new_po_lines.order_id.button_confirm()

        # On supplierinfo set product_uom_unit as min_qty_uom_id
        # Create procurement line with rule buy and quantity 17
        # run procurement
        self.sp_30.min_qty_uom_id = self.env.ref("uom.product_uom_unit")

        existing_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product_test.id)], order="id"
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_test,
                    17,
                    self.env.ref("uom.product_uom_unit"),
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        new_po_lines = self.env["purchase.order.line"].search(
            [
                ("product_id", "=", self.product_test.id),
                ("id", "not in", existing_po_lines.ids),
            ],
            order="id",
        )
        # Check product_purchase_uom_id is product_uom_unit
        # Check product_purchase_qty is 2
        # Check product_qty is 2
        # Check packaging_id is product_packaging_3
        # Check product_uom is product_uom_dozen
        self.assertEqual(
            self.env.ref("uom.product_uom_unit"), new_po_lines.product_purchase_uom_id,
        )
        self.assertEqual(2, new_po_lines.product_purchase_qty)
        self.assertEqual(2, new_po_lines.product_qty)
        self.assertEqual(self.product_packaging_3, new_po_lines.packaging_id)
        self.assertEqual(
            self.env.ref("uom.product_uom_dozen"), new_po_lines.product_uom,
        )
        self.assertEqual(3, new_po_lines.price_unit)
        # Confirm Purchase Order to avoid group
        new_po_lines.order_id.button_confirm()

        # Create procurement line with rule buy and quantity 1 dozen
        # set purcahse price to 36
        # run procurement
        self.sp_30.price = 36
        existing_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product_test.id)], order="id"
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_test,
                    1,
                    self.env.ref("uom.product_uom_dozen"),
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        new_po_lines = self.env["purchase.order.line"].search(
            [
                ("product_id", "=", self.product_test.id),
                ("id", "not in", existing_po_lines.ids),
            ],
            order="id",
        )
        # Check product_purchase_uom_id is product_uom_unit
        # Check product_purchase_qty is 1
        # Check product_qty is 1
        # Check packaging_id is product_packaging_3
        # Check product_uom is product_uom_dozen
        # Check price_unit is 3*12 = 36
        self.assertEqual(
            self.env.ref("uom.product_uom_unit"), new_po_lines.product_purchase_uom_id,
        )
        self.assertEqual(1, new_po_lines.product_purchase_qty)
        self.assertEqual(1, new_po_lines.product_qty)
        self.assertEqual(self.product_packaging_3, new_po_lines.packaging_id)
        self.assertEqual(
            self.env.ref("uom.product_uom_dozen"), new_po_lines.product_uom,
        )
        self.assertEqual(36, new_po_lines.price_unit)
        new_po_lines.order_id.button_confirm()

    def test_procurement_from_orderpoint_draft_po(self):
        # Define a multiple of 12 on supplier info
        # Trigger a stock minimum rule of 10 PC
        # A purchase line with 12 PC should be generated
        # Change the stock minimum to 11 PC
        # The purchase quantity should remains 12
        # Change the stock minimum to 13 PC
        # The purchase quantity should increase up to 24
        warehouse = self.env.ref("stock.warehouse0")
        product = self.product_test
        product.route_ids = [
            (4, self.env.ref("purchase_stock.route_warehouse0_buy").id)
        ]
        self.env.ref("uom.product_uom_dozen").rounding = 1
        procurement_obj = self.env["procurement.group"]

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.env.ref("uom.product_uom_dozen")

        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "warehouse_id": warehouse.id,
                "location_id": warehouse.lot_stock_id.id,
                "product_id": product.id,
                "product_min_qty": 10,
                "product_max_qty": 10,
            }
        )
        procurement_obj.run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("orderpoint_id", "=", orderpoint.id)]
        )
        self.assertEqual(len(new_po_lines), 1)
        self.assertEqual(new_po_lines.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 11
        orderpoint.product_max_qty = 11

        procurement_obj.run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("orderpoint_id", "=", orderpoint.id)]
        )

        self.assertEqual(len(new_po_lines), 1)
        self.assertEqual(new_po_lines.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 13
        orderpoint.product_max_qty = 13

        procurement_obj.run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("orderpoint_id", "=", orderpoint.id)]
        )

        self.assertEqual(len(new_po_lines), 1)
        self.assertEqual(new_po_lines.product_qty, 24)

    def test_procurement_from_orderpoint_sent_po(self):
        # Define a multiple of 12 on supplier info
        # Trigger a stock minimum rule of 10 PC
        # A purchase line with 12 PC should be generated
        # Send the purchase order
        # Change the stock minimum to 11 PC
        # No new purchase should be generated
        # Change the stock minimum to 13 PC
        # A new purchase should be generated
        warehouse = self.env.ref("stock.warehouse0")
        product = self.product_test
        product.route_ids = [
            (4, self.env.ref("purchase_stock.route_warehouse0_buy").id)
        ]
        self.env.ref("uom.product_uom_dozen").rounding = 1
        procurement_obj = self.env["procurement.group"]

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.env.ref("uom.product_uom_dozen")

        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "warehouse_id": warehouse.id,
                "location_id": warehouse.lot_stock_id.id,
                "product_id": product.id,
                "product_min_qty": 10,
                "product_max_qty": 10,
            }
        )
        procurement_obj.run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("orderpoint_id", "=", orderpoint.id)]
        )
        self.assertEqual(len(new_po_lines), 1)
        self.assertEqual(new_po_lines.product_qty, 12)

        new_po_lines.order_id.write({"state": "sent"})

        # change order_point level and rerun
        orderpoint.product_min_qty = 11
        orderpoint.product_max_qty = 11

        procurement_obj.run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("orderpoint_id", "=", orderpoint.id)]
        )

        self.assertEqual(len(new_po_lines), 1)
        self.assertEqual(new_po_lines.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 13
        orderpoint.product_max_qty = 13

        procurement_obj.run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("orderpoint_id", "=", orderpoint.id)]
        )

        self.assertEqual(len(new_po_lines), 2)

        for new_po_line in new_po_lines:
            self.assertEqual(new_po_line.product_qty, 12)

    def test_procurement_from_orderpoint_to_approve_po(self):
        # Define a multiple of 12 on supplier info
        # Trigger a stock minimum rule of 10 PC
        # A purchase line with 12 PC should be generated
        # Set the purchase order to approve
        # Change the stock minimum to 11 PC
        # No new purchase should be generated
        # Change the stock minimum to 13 PC
        # A new purchase should be generated
        warehouse = self.env.ref("stock.warehouse0")
        product = self.product_test
        product.route_ids = [
            (4, self.env.ref("purchase_stock.route_warehouse0_buy").id)
        ]
        self.env.ref("uom.product_uom_dozen").rounding = 1
        procurement_obj = self.env["procurement.group"]

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.env.ref("uom.product_uom_dozen")

        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "warehouse_id": warehouse.id,
                "location_id": warehouse.lot_stock_id.id,
                "product_id": product.id,
                "product_min_qty": 10,
                "product_max_qty": 10,
            }
        )
        procurement_obj.run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("orderpoint_id", "=", orderpoint.id)]
        )
        self.assertEqual(len(new_po_lines), 1)
        self.assertEqual(new_po_lines.product_qty, 12)

        new_po_lines.order_id.write({"state": "to approve"})

        # change order_point level and rerun
        orderpoint.product_min_qty = 11
        orderpoint.product_max_qty = 11

        procurement_obj.run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("orderpoint_id", "=", orderpoint.id)]
        )

        self.assertEqual(len(new_po_lines), 1)
        self.assertEqual(new_po_lines.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 13
        orderpoint.product_max_qty = 13

        procurement_obj.run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("orderpoint_id", "=", orderpoint.id)]
        )

        self.assertEqual(len(new_po_lines), 2)

        for new_po_line in new_po_lines:
            self.assertEqual(new_po_line.product_qty, 12)

    def test_procurement_from_orderpoint_confirmed_po(self):
        # Define a multiple of 12 on supplier info
        # Trigger a stock minimum rule of 10 PC
        # A purchase line with 12 PC should be generated
        # Confirm the purchase order
        # Change the stock minimum to 11 PC
        # No new purchase should be generated
        # Change the stock minimum to 13 PC
        # A new purchase should be generated
        warehouse = self.env.ref("stock.warehouse0")
        product = self.product_test
        product.route_ids = [
            (4, self.env.ref("purchase_stock.route_warehouse0_buy").id)
        ]
        self.env.ref("uom.product_uom_dozen").rounding = 1
        procurement_obj = self.env["procurement.group"]

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.env.ref("uom.product_uom_dozen")

        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "warehouse_id": warehouse.id,
                "location_id": warehouse.lot_stock_id.id,
                "product_id": product.id,
                "product_min_qty": 10,
                "product_max_qty": 10,
            }
        )
        procurement_obj.run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("orderpoint_id", "=", orderpoint.id)]
        )
        self.assertEqual(len(new_po_lines), 1)
        self.assertEqual(new_po_lines.product_qty, 12)

        new_po_lines.order_id.button_confirm()

        # change order_point level and rerun
        orderpoint.product_min_qty = 11
        orderpoint.product_max_qty = 11

        procurement_obj.run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("orderpoint_id", "=", orderpoint.id)]
        )

        self.assertEqual(len(new_po_lines), 1)
        self.assertEqual(new_po_lines.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 13
        orderpoint.product_max_qty = 13

        procurement_obj.run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("orderpoint_id", "=", orderpoint.id)]
        )

        self.assertEqual(len(new_po_lines), 2)

        for new_po_line in new_po_lines:
            self.assertEqual(new_po_line.product_qty, 12)

    def test_procurement_kg(self):
        partner = self.env.ref("base.res_partner_2")
        uom_kg = self.env.ref("uom.product_uom_kgm")
        product = self.env["product.product"].create(
            {
                "name": "Orange",
                "uom_id": uom_kg.id,
                "uom_po_id": uom_kg.id,
                "route_ids": [
                    (4, self.env.ref("purchase_stock.route_warehouse0_buy").id)
                ],
                "seller_ids": [
                    (
                        0,
                        0,
                        {"name": partner.id, "price": 20, "min_qty_uom_id": uom_kg.id},
                    )
                ],
            }
        )

        existing_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", product.id)], order="id"
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    product,
                    17.3,
                    uom_kg,
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        self.env["procurement.group"].run_scheduler()
        new_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", product.id), ("id", "not in", existing_po_lines.ids)],
            order="id",
        )
        self.assertEqual(uom_kg, new_po_lines.product_purchase_uom_id)
        self.assertEqual(17.3, new_po_lines.product_purchase_qty)
        self.assertEqual(17.3, new_po_lines.product_qty)
        self.assertEqual(uom_kg, new_po_lines.product_uom)
        self.assertEqual(20, new_po_lines.price_unit)

    def test_procurement_kg_multiple(self):
        partner = self.env.ref("base.res_partner_2")
        uom_kg = self.env.ref("uom.product_uom_kgm")
        uom_20_kg = self.env["uom.uom"].create(
            {
                "category_id": self.env.ref("uom.product_uom_categ_kgm").id,
                "name": "20 KG",
                "factor_inv": 20,
                "uom_type": "bigger",
                "rounding": 1.0,
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "Orange",
                "uom_id": uom_kg.id,
                "uom_po_id": uom_kg.id,
                "route_ids": [
                    (4, self.env.ref("purchase_stock.route_warehouse0_buy").id)
                ],
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": partner.id,
                            "price": 20,
                            "min_qty": 1,
                            "product_uom": uom_20_kg.id,
                            "min_qty_uom_id": uom_20_kg.id,
                        },
                    )
                ],
            }
        )
        existing_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", product.id)], order="id"
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    product,
                    17.3,
                    uom_kg,
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        new_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", product.id), ("id", "not in", existing_po_lines.ids)],
            order="id",
        )

        self.assertEqual(uom_20_kg, new_po_lines.product_purchase_uom_id)
        self.assertEqual(1, new_po_lines.product_purchase_qty)
        self.assertEqual(20, new_po_lines.product_qty)
        self.assertEqual(uom_kg, new_po_lines.product_uom)
        self.assertEqual(20, new_po_lines.price_unit)

    def test_procurement_kg_packaging(self):
        partner = self.env.ref("base.res_partner_2")
        uom_kg = self.env.ref("uom.product_uom_kgm")

        uom_20_kg = self.env["uom.uom"].create(
            {
                "category_id": self.env.ref("uom.product_uom_categ_kgm").id,
                "name": "20 KG",
                "factor_inv": 20,
                "uom_type": "bigger",
                "rounding": 1.0,
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "Orange",
                "uom_id": uom_kg.id,
                "uom_po_id": uom_kg.id,
                "route_ids": [
                    (4, self.env.ref("purchase_stock.route_warehouse0_buy").id)
                ],
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": partner.id,
                            "price": 20,
                            "min_qty": 0,
                            "min_qty_uom_id": uom_kg.id,
                            "product_uom": uom_kg.id,
                        },
                    )
                ],
            }
        )

        product_packaging_20 = self.env["product.packaging"].create(
            {
                "product_id": product.id,
                "uom_id": uom_20_kg.id,
                "name": "Packaging Dozen",
            }
        )
        product.seller_ids[0].packaging_id = product_packaging_20

        existing_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", product.id)], order="id"
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    product,
                    17.3,
                    uom_kg,
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        new_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", product.id), ("id", "not in", existing_po_lines.ids)],
            order="id",
        )
        self.assertEqual(uom_kg, new_po_lines.product_purchase_uom_id)
        self.assertEqual(1, new_po_lines.product_purchase_qty)
        self.assertEqual(1, new_po_lines.product_qty)
        self.assertEqual(uom_20_kg, new_po_lines.product_uom)
        self.assertEqual(product_packaging_20, new_po_lines.packaging_id)
        self.assertEqual(20, new_po_lines.price_unit)

    def test_procurement_regrouped_po(self):
        """
        Product must be bought per 8 units Package
        1/ run a procurement for 4 units
        A po lines must be generate for 1 package of 8 units
        2/ run a new procurement for 4 units
        The po line should remain unchanged as the first rounding value is
        enough
        """
        self.product_test.route_ids = [
            (4, self.env.ref("purchase_stock.route_warehouse0_buy").id)
        ]
        self.env.ref("uom.product_uom_unit").rounding = 1

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.product_uom_8
        self.sp_30.price = 3
        existing_po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product_test.id)], order="id"
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_test,
                    4,
                    self.env.ref("uom.product_uom_unit"),
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        new_po_lines = self.env["purchase.order.line"].search(
            [
                ("product_id", "=", self.product_test.id),
                ("id", "not in", existing_po_lines.ids),
            ],
            order="id",
        )
        self.assertEqual(
            self.product_uom_8, new_po_lines.product_purchase_uom_id,
        )
        self.assertEqual(1, new_po_lines.product_purchase_qty)
        self.assertEqual(8, new_po_lines.product_qty)
        self.assertEqual(4, new_po_lines.product_qty_needed)
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_test,
                    4,
                    self.env.ref("uom.product_uom_unit"),
                    self.env.ref("stock.stock_location_stock"),
                    "/",
                    "/",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": fields.Date.today(),
                    },
                )
            ]
        )
        self.assertEqual(
            self.product_uom_8, new_po_lines.product_purchase_uom_id,
        )
        self.assertEqual(1, new_po_lines.product_purchase_qty)
        self.assertEqual(8, new_po_lines.product_qty_needed)
        self.assertEqual(8, new_po_lines.product_qty)
