# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import SavepointCase


class TestStockOrderpointTemplate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.productA = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "consu",
            }
        )
        cls.productB = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "consu",
            }
        )
        cls.productC = cls.env["product.product"].create(
            {
                "name": "Product C",
                "type": "consu",
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})

    def test_stock_orderpoint_template_orderpoint_creation(self):
        warehouse = self.env["stock.warehouse"].search([], limit=1)

        template = self.env["stock.warehouse.orderpoint.template"].create(
            {
                "location_id": warehouse.lot_stock_id.id,
                "product_min_qty": 0.0,
                "product_max_qty": 15.0,
            }
        )
        self.assertFalse(
            self.env["stock.warehouse.orderpoint"].search(
                [("product_id", "=", self.productA.id)]
            )
        )

        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": warehouse.out_type_id.id,
                "location_id": warehouse.lot_stock_id.id,
                "location_dest_id": self.ref("stock.stock_location_customers"),
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Delivery",
                            "product_id": self.productA.id,
                            "product_uom": self.uom_unit.id,
                            "product_uom_qty": 12.0,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()

        orderpoint = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", self.productA.id)]
        )

        self.assertTrue(orderpoint)
        self.assertEqual(orderpoint.template_id, template)
        self.assertEqual(orderpoint.product_min_qty, 0.0)
        self.assertEqual(orderpoint.product_max_qty, 15.0)
        self.assertEqual(orderpoint.warehouse_id, warehouse)
        self.assertEqual(orderpoint.location_id, warehouse.lot_stock_id)
        self.assertEqual(orderpoint.company_id, warehouse.company_id)
        self.assertEqual(orderpoint.trigger, "auto")

        receipt_move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.productA.id),
                ("location_id", "=", self.env.ref("stock.stock_location_suppliers").id),
            ]
        )
        self.assertTrue(receipt_move)
        self.assertEqual(receipt_move.date.date(), date.today())
        self.assertEqual(receipt_move.product_uom_qty, 27.0)

    def test_stock_orderpoint_template_orderpoint_priority(self):
        warehouse = self.env["stock.warehouse"].search([], limit=1)

        self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.productA.id,
                "location_id": warehouse.lot_stock_id.id,
                "product_min_qty": 0.0,
                "product_max_qty": 5.0,
            }
        )

        self.env["stock.warehouse.orderpoint.template"].create(
            {
                "location_id": warehouse.lot_stock_id.id,
                "product_min_qty": 0.0,
                "product_max_qty": 15.0,
            }
        )

        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": warehouse.out_type_id.id,
                "location_id": warehouse.lot_stock_id.id,
                "location_dest_id": self.ref("stock.stock_location_customers"),
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Delivery",
                            "product_id": self.productA.id,
                            "product_uom": self.uom_unit.id,
                            "product_uom_qty": 12.0,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()

        receipt_move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.productA.id),
                ("location_id", "=", self.env.ref("stock.stock_location_suppliers").id),
            ]
        )
        self.assertTrue(receipt_move)
        self.assertEqual(receipt_move.date.date(), date.today())
        self.assertEqual(receipt_move.product_uom_qty, 17.0)

    def test_stock_orderpoint_template_orderpoint_propagate_modifications(self):
        warehouse = self.env["stock.warehouse"].search([], limit=1)

        orderpointA = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.productA.id,
                "location_id": warehouse.lot_stock_id.id,
                "product_min_qty": 0.0,
                "product_max_qty": 5.0,
            }
        )

        template = self.env["stock.warehouse.orderpoint.template"].create(
            {
                "location_id": warehouse.lot_stock_id.id,
                "product_min_qty": 0.0,
                "product_max_qty": 15.0,
            }
        )
        orderpointB = template._create_orderpoint(self.productB)
        orderpointC = template._create_orderpoint(self.productC)

        self.assertEqual(orderpointA.product_min_qty, 0.0)
        self.assertEqual(orderpointA.product_max_qty, 5.0)
        self.assertEqual(orderpointB.product_min_qty, 0.0)
        self.assertEqual(orderpointB.product_max_qty, 15.0)
        self.assertEqual(orderpointC.product_min_qty, 0.0)
        self.assertEqual(orderpointC.product_max_qty, 15.0)

        template.write({"product_min_qty": 5.0, "product_max_qty": 10.0})

        self.assertEqual(orderpointA.product_min_qty, 0.0)
        self.assertEqual(orderpointA.product_max_qty, 5.0)
        self.assertEqual(orderpointB.product_min_qty, 5.0)
        self.assertEqual(orderpointB.product_max_qty, 10.0)
        self.assertEqual(orderpointC.product_min_qty, 5.0)
        self.assertEqual(orderpointC.product_max_qty, 10.0)
