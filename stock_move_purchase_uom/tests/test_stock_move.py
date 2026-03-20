# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import Command
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

    def test_create_move_same_uom_rounding_up(self):
        unit_uom = self.env.ref("uom.product_uom_unit")
        unit_uom.rounding = 1.0
        product_unit = self.env["product.product"].create(
            {
                "name": "Test product unit",
                "is_storable": True,
                "categ_id": self.env.ref("product.product_category_all").id,
                "uom_id": unit_uom.id,
                "uom_po_id": unit_uom.id,
            }
        )
        self.stock_picking_type_2.purchase_uom_rounding_method = "UP"
        move = self.env["stock.move"].create(
            {
                "name": product_unit.display_name,
                "location_id": self.location.id,
                "location_dest_id": self.location_dest.id,
                "product_id": product_unit.id,
                "product_uom_qty": 5.25,
                "picking_type_id": self.stock_picking_type_2.id,
                "product_uom": unit_uom.id,
            }
        )
        self.assertEqual(move.product_uom_qty, 6.0)

    def test_create_move_same_uom_rounding_half_up(self):
        unit_uom = self.env.ref("uom.product_uom_unit")
        unit_uom.rounding = 1.0
        product_unit = self.env["product.product"].create(
            {
                "name": "Test product unit",
                "is_storable": True,
                "categ_id": self.env.ref("product.product_category_all").id,
                "uom_id": unit_uom.id,
                "uom_po_id": unit_uom.id,
            }
        )
        self.stock_picking_type_2.purchase_uom_rounding_method = "HALF-UP"
        move = self.env["stock.move"].create(
            {
                "name": product_unit.display_name,
                "location_id": self.location.id,
                "location_dest_id": self.location_dest.id,
                "product_id": product_unit.id,
                "product_uom_qty": 5.25,
                "picking_type_id": self.stock_picking_type_2.id,
                "product_uom": unit_uom.id,
            }
        )
        self.assertEqual(move.product_uom_qty, 5.0)

    def test_create_move_linked_sml_not_unreserved(self):
        # The UoM conversion in create must not trigger unreservation of
        # explicitly linked SML
        sml = self.env["stock.move.line"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.cm_uom.id,
                "quantity": 70,
                "location_id": self.location.id,
                "location_dest_id": self.location_dest.id,
                "company_id": self.env.company.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.product.display_name,
                "location_id": self.location.id,
                "location_dest_id": self.location_dest.id,
                "product_id": self.product.id,
                "product_uom_qty": 30,
                "product_uom": self.cm_uom.id,
                "picking_type_id": self.stock_picking_type_2.id,
                "state": "assigned",
                "move_line_ids": [Command.link(sml.id)],
            }
        )
        self.assertTrue(sml.exists())
        self.assertEqual(sml.move_id, move)
        # UoM was converted on the SM but not on the SML
        self.assertEqual(move.product_uom, self.meter_uom)
        self.assertEqual(sml.product_uom_id, self.cm_uom)
        # SML quantity is unchanged (70 cm)
        self.assertEqual(sml.quantity, 70)
        # SM demand converted: 30 cm --> 0.3 m
        self.assertEqual(move.product_uom_qty, 0.3)
        # SM reserved qty is computed from SML: 70 cm --> 0.7 m
        # Quantities are coherent, but SML is kept as original
        self.assertEqual(move.quantity, 0.7)
