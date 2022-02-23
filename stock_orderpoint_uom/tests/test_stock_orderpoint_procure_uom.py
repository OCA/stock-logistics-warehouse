# Copyright 2016-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.exceptions import ValidationError
from odoo.tools import mute_logger


class TestStockOrderpointProcureUom(common.TransactionCase):
    def setUp(self):
        super(TestStockOrderpointProcureUom, self).setUp()

        # Get required Model
        productObj = self.env["product.product"]
        self.purchase_model = self.env["purchase.order"]
        self.purchase_line_model = self.env["purchase.order.line"]
        self.warehouse = self.env.ref("stock.warehouse0")
        self.location_stock = self.env.ref("stock.stock_location_stock")
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.uom_unit.rounding = 1
        self.uom_dozen = self.env.ref("uom.product_uom_dozen")
        self.uom_dozen.rounding = 1
        self.uom_kg = self.env.ref("uom.product_uom_kgm")

        self.productA = productObj.create(
            {
                "name": "product A",
                "standard_price": 1,
                "type": "product",
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_dozen.id,
                "default_code": "A",
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

    def test_01_stock_orderpoint_procure_uom(self):

        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "warehouse_id": self.warehouse.id,
                "location_id": self.location_stock.id,
                "product_id": self.productA.id,
                "product_max_qty": 24,
                "product_min_qty": 12,
                "product_uom": self.uom_unit.id,
                "procure_uom_id": self.uom_dozen.id,
            }
        )

        self.env["procurement.group"].run_scheduler()
        # As per route configuration, it will create Purchase order
        purchase = self.purchase_model.search([("origin", "ilike", orderpoint.name)])
        self.assertEqual(len(purchase), 1)
        purchase_line = self.purchase_line_model.search(
            [("orderpoint_id", "=", orderpoint.id), ("order_id", "=", purchase.id)]
        )
        self.assertEqual(len(purchase_line), 1)
        self.assertEqual(purchase_line.product_id, self.productA)
        self.assertEqual(purchase_line.product_uom, self.uom_dozen)
        self.assertEqual(purchase_line.product_qty, 2)

    def test_02_stock_orderpoint_wrong_uom(self):

        with mute_logger("openerp.sql_db"):
            with self.assertRaises(ValidationError):
                self.env["stock.warehouse.orderpoint"].create(
                    {
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.location_stock.id,
                        "product_id": self.productA.id,
                        "product_max_qty": 24,
                        "product_min_qty": 12,
                        "procure_uom_id": self.uom_kg.id,
                    }
                )

    def test_03_regenerate_po(self):
        def _assert_purchase_generated(self, supplier, product):
            purchase = self.purchase_model.search([("partner_id", "=", supplier.id)])
            self.assertEqual(len(purchase), 1)
            lines = purchase.order_line
            self.assertEqual(len(lines), 1)
            self.assertEqual(lines.product_id, product)
            self.assertEqual(lines.product_uom, self.uom_dozen)
            self.assertEqual(lines.product_qty, 9)
            return purchase

        supplier = self.env["res.partner"].create(
            {"name": "Brewery Inc", "is_company": True}
        )

        product = self.env["product.product"].create(
            {
                "name": "Beer bottle",
                "standard_price": 1,
                "type": "product",
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_dozen.id,
                "seller_ids": [
                    (
                        0,
                        False,
                        {"name": supplier.id, "delay": 1, "min_qty": 1, "price": 2},
                    )
                ],
            }
        )

        self.env["stock.warehouse.orderpoint"].create(
            {
                "warehouse_id": self.warehouse.id,
                "location_id": self.location_stock.id,
                "product_id": product.id,
                "product_max_qty": 100,
                "product_min_qty": 10,
                "qty_multiple": 10,
                "product_uom": self.uom_unit.id,
                "procure_uom_id": self.uom_dozen.id,
            }
        )

        self.env["procurement.group"].run_scheduler()

        purchase1 = _assert_purchase_generated(self, supplier, product)
        purchase1.button_cancel()
        purchase1.unlink()

        self.env["procurement.group"].run_scheduler()

        _assert_purchase_generated(self, supplier, product)
