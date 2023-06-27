# Copyright 2023 ForgeFlow S.L (https://www.forgeflow.com)

from odoo.tests.common import Form, TransactionCase


class TestStockQuantReservationInfoMrp(TransactionCase):
    def setUp(self):
        super().setUp()

        self.partner = self.env["res.partner"].create({"name": "Jean"})
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        uom_unit = self.env.ref("uom.product_uom_unit")

        self.product_1 = self.env["product.product"].create(
            {"name": "Product 1", "type": "product", "uom_id": uom_unit.id}
        )
        self.prod_tp1 = self.env["product.product"].create(
            {
                "name": "Test Product Built",
                "type": "product",
                "list_price": 150.0,
                "uom_id": uom_unit.id,
            }
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

        self.test_bom_1 = self.env["mrp.bom"].create(
            {
                "product_id": self.prod_tp1.id,
                "product_tmpl_id": self.prod_tp1.product_tmpl_id.id,
                "product_uom_id": self.prod_tp1.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        self.env["mrp.bom.line"].create(
            {
                "bom_id": self.test_bom_1.id,
                "product_id": self.product_1.id,
                "product_qty": 5.0,
            }
        )

    def test_01_StockQuantReservationInfoMrp(self):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.prod_tp1
        mo_form.bom_id = self.test_bom_1
        mo_form.product_qty = 1.0
        mo_form.product_uom_id = self.prod_tp1.uom_id
        main_mo = mo_form.save()
        main_mo.action_confirm()

        self.assertEqual(self.product_1.stock_quant_ids[1].reserved_quantity, 0.0)

        main_mo.action_assign()

        self.assertEqual(self.product_1.stock_quant_ids[1].reserved_quantity, 5.0)

        action = self.product_1.stock_quant_ids[1].action_reserved_moves()
        move_line_post_a = self.env["stock.move.line"].search(action["domain"])

        action2 = move_line_post_a.action_view_mrp_from_reserved()
        self.assertEqual(action2["res_id"], main_mo.id)
