# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import common


class TestMoveLocationPurchaseUom(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location_obj = cls.env["stock.location"]
        product_obj = cls.env["product.product"]
        cls.wizard_obj = cls.env["wiz.stock.move.location"]
        cls.quant_obj = cls.env["stock.quant"]
        cls.company = cls.env.ref("base.main_company")
        cls.partner = cls.env.ref("base.res_partner_category_0")

        cls.internal_loc_1 = cls.location_obj.create(
            {
                "name": "INT_1",
                "usage": "internal",
                "active": True,
                "company_id": cls.company.id,
            }
        )
        cls.internal_loc_2 = cls.location_obj.create(
            {
                "name": "INT_2",
                "usage": "internal",
                "active": True,
                "company_id": cls.company.id,
            }
        )
        cls.stock_picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Internal transfer 2",
                "code": "internal",
                "sequence_code": "INT2",
                "use_purchase_uom": True,
            }
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = product_obj.create(
            {
                "name": "Test",
                "type": "product",
            }
        )

        cls.set_product_amount(cls.product, cls.internal_loc_1, 70)

    @classmethod
    def set_product_amount(
        cls, product, location, amount, lot_id=None, package_id=None, owner_id=None
    ):
        cls.env["stock.quant"]._update_available_quantity(
            product,
            location,
            amount,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
        )

    @classmethod
    def _create_wizard(cls, origin_location, destination_location):
        move_location_wizard = cls.env["wiz.stock.move.location"]
        return move_location_wizard.create(
            {
                "origin_location_id": origin_location.id,
                "destination_location_id": destination_location.id,
            }
        )

    def test_move_location_purchase_uom(self):
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.onchange_origin_location()
        self.assertEqual(len(wizard.stock_move_location_line_ids), 1)
        line = wizard.stock_move_location_line_ids[0]
        self.assertEqual(line.product_uom_id, self.product.uom_id)
        original_picking_type = wizard.picking_type_id

        # Change the picking type to one that must use purchase uom
        wizard.picking_type_id = self.stock_picking_type
        wizard._onchange_picking_type_id()

        # Check that the uom and quantities have changed
        original_uom = line.product_uom_id
        original_move_qty = line.move_quantity
        original_max_qty = line.max_quantity
        original_reserved_qty = line.reserved_quantity
        expected_move_quantity = original_uom._compute_quantity(
            original_move_qty, self.product.uom_po_id
        )
        expected_max_quantity = original_uom._compute_quantity(
            original_max_qty, self.product.uom_po_id
        )
        expected_reserved_quantity = original_uom._compute_quantity(
            original_reserved_qty, self.product.uom_po_id
        )
        self.assertEqual(line.product_uom_id, self.product.uom_po_id)
        self.assertEqual(line.move_quantity, expected_move_quantity)
        self.assertEqual(line.max_quantity, expected_max_quantity)
        self.assertEqual(line.reserved_quantity, expected_reserved_quantity)

        # Change again to the first picking type that does not use purchase uom
        wizard.picking_type_id = original_picking_type
        wizard._onchange_picking_type_id()
        self.assertEqual(line.product_uom_id, self.product.uom_id)
        self.assertEqual(line.move_quantity, original_move_qty)
        self.assertEqual(line.max_quantity, original_max_qty)
        self.assertEqual(line.reserved_quantity, original_reserved_qty)

        # Check the creation of the move with a picking type using purchase uom
        wizard.picking_type_id = self.stock_picking_type
        wizard._onchange_picking_type_id()
        wizard.action_move_location()
        picking = wizard.picking_id
        self.assertEqual(len(picking.move_line_ids), 1)
        picking_line = picking.move_line_ids[0]
        self.assertEqual(picking_line.product_uom_id, self.product.uom_po_id)
        self.assertEqual(picking_line.qty_done, expected_move_quantity)
