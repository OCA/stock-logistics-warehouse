# Copyright 2023 ForgeFlow S.L (https://www.forgeflow.com)

from odoo.tests.common import TransactionCase


class TestStockQuantReservationInfo(TransactionCase):
    def setUp(self):
        super().setUp()

        self.partner = self.env["res.partner"].create({"name": "Jean"})
        self.partner_customer = self.env["res.partner"].create({"name": "Nate"})
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        uom_unit = self.env.ref("uom.product_uom_unit")

        self.product_1 = self.env["product.product"].create(
            {"name": "Product 1", "type": "product", "uom_id": uom_unit.id}
        )
        self.receipt = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
            }
        )
        move_receipt_1 = self.env["stock.move"].create(
            {
                "name": "Test 1",
                "product_id": self.product_1.id,
                "quantity_done": 20,
                "product_uom": self.product_1.uom_id.id,
                "picking_id": self.receipt.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        move_receipt_1._action_confirm()
        self.receipt.button_validate()

    def test_01_StockQuantReservationInfo(self):

        self.delivery = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.partner_customer.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        customer_move = self.env["stock.move"].create(
            {
                "name": "move out",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "product_id": self.product_1.id,
                "product_uom": self.product_1.uom_id.id,
                "product_uom_qty": 10.0,
                "picking_id": self.delivery.id,
            }
        )
        customer_move._action_confirm()

        move_lines_ini = self.env["stock.move.line"].search(
            [("picking_id", "=", self.delivery.id)]
        )
        self.assertFalse(move_lines_ini)
        self.assertEqual(self.product_1.stock_quant_ids[1].reserved_quantity, 0.0)

        self.delivery.action_assign()

        self.assertEqual(self.product_1.stock_quant_ids[1].reserved_quantity, 10.0)

        # we execute manually the method executed by the first button just to get the domain
        action = self.product_1.stock_quant_ids[1].action_reserved_moves()
        move_line_post_a = self.env["stock.move.line"].search(action["domain"])

        # we execute manually the second button to see if the method
        # returns the same stock picking form as the delivery picking
        action2 = move_line_post_a.action_view_picking_from_reserved()

        self.assertEqual(action2["res_id"], self.delivery.id)
        move_line_post_b = self.env["stock.move.line"].search(
            [("picking_id", "=", self.delivery.id)]
        )
        self.assertTrue(move_line_post_a)
        self.assertEqual(move_line_post_a, move_line_post_b)
