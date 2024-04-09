# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import Form

from .test_common import TestCommon


class TestStockMovePurchaseUom(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.stock_picking_type_2 = cls.env["stock.picking.type"].create(
            {
                "name": "Internal transfer 2",
                "code": "internal",
                "sequence_code": "INT",
                "use_purchase_uom": True,
                "show_operations": True,
            }
        )

    def test_stock_move_purchase_uom_unlinked_move_line(self):
        picking_form = Form(self.env["stock.picking"])
        picking_form.partner_id = self.partner
        picking_form.picking_type_id = self.stock_picking_type_2
        picking_form.location_id = self.location
        picking_form.location_dest_id = self.location_dest
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.product
            self.assertEqual(move.product_uom.id, self.product.uom_po_id.id)
        picking = picking_form.save()
        picking.action_confirm()
        with Form(picking) as picking_form:
            with picking_form.move_line_ids_without_package.new() as move_line:
                move_line.product_id = self.product
                # Since the line is not being linked to the move (move_id is false)
                # the uom to set is the product purchase uom.
                self.assertEqual(move_line.product_uom_id.id, self.product.uom_po_id.id)

    def test_stock_move_purchase_uom_linked_move_line(self):
        self.stock_picking_type_2.show_operations = False
        picking_form = Form(self.env["stock.picking"])
        picking_form.partner_id = self.partner
        picking_form.picking_type_id = self.stock_picking_type_2
        picking_form.location_id = self.location
        picking_form.location_dest_id = self.location_dest
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.product
            self.assertEqual(move.product_uom.id, self.product.uom_po_id.id)
            move.product_uom = self.product.uom_id
            self.assertEqual(move.product_uom.id, self.product.uom_id.id)
        picking = picking_form.save()
        picking.action_confirm()
        move = picking.move_ids_without_package[0]
        with Form(
            move, view=self.env.ref("stock.view_stock_move_operations")
        ) as move_form:
            with move_form.move_line_ids.new() as move_line:
                move_line.product_id = self.product
                # Since the line is being linked to the move the uom used will be the move one.
                self.assertEqual(
                    move_line.product_uom_id.id, move_line.move_id.product_uom.id
                )
