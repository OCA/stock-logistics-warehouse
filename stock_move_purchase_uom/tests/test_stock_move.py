# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import Form

from .test_common import TestCommon


class TestStockMove(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_onchange_product_id(self):
        self.stock_move._onchange_product_id()
        self.assertEqual(self.stock_move.product_uom.id, self.product.uom_id.id)

        self.stock_picking_type.use_purchase_uom = True

        self.stock_move._onchange_product_id()
        self.assertEqual(self.stock_move.product_uom.id, self.product.uom_po_id.id)

    def test_create_move_rounding_method_half_up(self):
        picking_form = Form(self.env["stock.picking"])
        picking_form.partner_id = self.partner
        picking_form.picking_type_id = self.stock_picking_type_2
        picking_form.location_id = self.location
        picking_form.location_dest_id = self.location_dest
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.product
            move.product_uom = self.cm_uom
            move.product_uom_qty = 0.4
        picking = picking_form.save()
        move = picking.move_ids_without_package[0]
        self.assertEqual(move.product_uom_qty, 0.0)

    def test_create_move_rounding_method_up(self):
        self.stock_picking_type_2.purchase_uom_rounding_method = "UP"
        picking_form = Form(self.env["stock.picking"])
        picking_form.partner_id = self.partner
        picking_form.picking_type_id = self.stock_picking_type_2
        picking_form.location_id = self.location
        picking_form.location_dest_id = self.location_dest
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.product
            move.product_uom = self.cm_uom
            move.product_uom_qty = 0.4
        picking = picking_form.save()
        move = picking.move_ids_without_package[0]
        self.assertEqual(move.product_uom_qty, 0.01)
