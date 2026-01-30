from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestStockMoveLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
            }
        )
        cls.stock_location = cls.env["stock.location"].create(
            {
                "name": "Test Location",
            }
        )
        cls.picking_type = cls.env["stock.picking.type"].create(
            {"name": "Test Picking Type", "code": "outgoing", "sequence_code": "SPT"}
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.stock_location.id,
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": "Test Move",
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.product.uom_id.id,
                            "move_line_ids": [
                                Command.create(
                                    {
                                        "product_id": cls.product.id,
                                        "product_uom_id": cls.product.uom_id.id,
                                    }
                                )
                            ],
                        }
                    )
                ],
            }
        )

    def test_linked_reference_with_picking(self):
        move_line = self.picking.move_ids_without_package.move_line_ids
        self.assertEqual(
            move_line.linked_reference,
            self.picking,
            "linked_reference should point to the picking when available",
        )

    def test_linked_reference_with_move(self):
        move = self.picking.move_ids_without_package
        move_line = move.move_line_ids
        move.picking_id = False
        self.assertEqual(
            move_line.linked_reference,
            move,
            "linked_reference should point to the move when picking is not available",
        )

    def test_linked_reference_no_reference(self):
        move_line = self.picking.move_ids_without_package.move_line_ids
        move_line.move_id = False
        self.assertFalse(
            move_line.linked_reference,
            "linked_reference should be False if no picking or move is available",
        )
