# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestStockPickingMTO(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mto_route = cls.env.ref("stock.route_warehouse0_mto")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test MTO Product",
                "route_ids": [Command.set(cls.mto_route.ids)],
                "type": "product",
            }
        )
        cls.wh_obj = cls.env["stock.warehouse"]
        cls.wh1 = cls.wh_obj.create({"name": "Test WH1", "code": "TSWH1"})
        cls.wh2 = cls.wh_obj.create(
            {
                "name": "Test WH2",
                "code": "TSWH2",
                "resupply_wh_ids": [Command.set(cls.wh1.ids)],
            }
        )
        cls.procurement_rule = cls.env["stock.rule"].create(
            {
                "name": "TST-WH1 -> TST-WH2 MTO",
                "route_id": cls.mto_route.id,
                "action": "pull",
                "location_src_id": cls.wh1.lot_stock_id.id,
                "procure_method": "make_to_stock",
                "picking_type_id": cls.wh1.int_type_id.id,
                "location_dest_id": cls.wh2.lot_stock_id.id,
                "warehouse_id": cls.wh2.id,
                "group_propagation_option": "propagate",
                "propagate_cancel": True,
                "propagate_warehouse_id": cls.wh1.id,
            }
        )
        cls.picking_obj = cls.env["stock.picking"].with_context(planned_picking=True)
        cls.picking = cls.picking_obj.create(
            {
                "picking_type_id": cls.wh1.int_type_id.id,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.wh2.lot_stock_id.id,
            }
        )

    def test_compute_procure_method(self):
        # No moves
        self.assertFalse(self.picking.procure_method)
        # A new move defaults to MTS
        move_line = self.env["stock.move"].create(
            {
                "name": "TSTMOVE001",
                "picking_id": self.picking.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 100,
                "location_id": self.wh1.lot_stock_id.id,
                "location_dest_id": self.wh2.lot_stock_id.id,
            }
        )
        self.assertEqual(self.picking.procure_method, "make_to_stock")
        # Change move procure method to MTO
        move_line.procure_method = "make_to_order"
        self.assertEqual(self.picking.procure_method, "make_to_order")
        # Add a new line with MTS rule
        move_line.copy({"procure_method": "make_to_stock"})
        self.assertFalse(self.picking.procure_method)
        # We set the procure method in the picking
        self.picking.procure_method = "make_to_order"
        self.assertEqual(self.picking.move_ids[1].procure_method, "make_to_order")

    def test_multiple_moves_same_procure_method(self):
        """Test picking with multiple moves having the same procure method."""
        # Create multiple MTS moves
        for i in range(3):
            self.env["stock.move"].create(
                {
                    "name": f"TSTMOVE00{i}",
                    "picking_id": self.picking.id,
                    "product_id": self.product.id,
                    "product_uom": self.product.uom_id.id,
                    "product_uom_qty": 10 * (i + 1),
                    "location_id": self.wh1.lot_stock_id.id,
                    "location_dest_id": self.wh2.lot_stock_id.id,
                    "procure_method": "make_to_stock",
                }
            )
        # All moves are MTS, so picking should be MTS
        self.assertEqual(self.picking.procure_method, "make_to_stock")
        self.assertEqual(len(self.picking.move_ids), 3)

        # Change all to MTO
        self.picking.move_ids.write({"procure_method": "make_to_order"})
        self.assertEqual(self.picking.procure_method, "make_to_order")

    def test_inverse_procure_method_with_false_value(self):
        """Test that setting procure_method to False doesn't update moves."""
        # Create moves with different procure methods
        self.env["stock.move"].create(
            {
                "name": "TSTMOVE_MTS",
                "picking_id": self.picking.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10,
                "location_id": self.wh1.lot_stock_id.id,
                "location_dest_id": self.wh2.lot_stock_id.id,
                "procure_method": "make_to_stock",
            }
        )
        self.env["stock.move"].create(
            {
                "name": "TSTMOVE_MTO",
                "picking_id": self.picking.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 20,
                "location_id": self.wh1.lot_stock_id.id,
                "location_dest_id": self.wh2.lot_stock_id.id,
                "procure_method": "make_to_order",
            }
        )
        # Picking should be False (mixed)
        self.assertFalse(self.picking.procure_method)

        # Store original procure methods
        original_methods = self.picking.move_ids.mapped("procure_method")

        # Try to set procure_method to False - should not change moves
        self.picking.procure_method = False

        # Moves should keep their original values
        self.assertEqual(
            self.picking.move_ids.mapped("procure_method"), original_methods
        )

    def test_selection_procure_method(self):
        """Test that _selection_procure_method returns correct values."""
        selection = self.picking._selection_procure_method()
        # Should return the same selection as stock.move procure_method field
        move_selection = self.env["stock.move"].fields_get(
            allfields=["procure_method"]
        )["procure_method"]["selection"]
        self.assertEqual(selection, move_selection)
        # Verify it contains the expected values
        selection_values = [s[0] for s in selection]
        self.assertIn("make_to_stock", selection_values)
        self.assertIn("make_to_order", selection_values)

    def test_move_removal_recalculation(self):
        """Test that procure_method is recalculated when moves are removed."""
        # Create two MTO moves
        move1 = self.env["stock.move"].create(
            {
                "name": "TSTMOVE001",
                "picking_id": self.picking.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10,
                "location_id": self.wh1.lot_stock_id.id,
                "location_dest_id": self.wh2.lot_stock_id.id,
                "procure_method": "make_to_order",
            }
        )
        move2 = self.env["stock.move"].create(
            {
                "name": "TSTMOVE002",
                "picking_id": self.picking.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 20,
                "location_id": self.wh1.lot_stock_id.id,
                "location_dest_id": self.wh2.lot_stock_id.id,
                "procure_method": "make_to_order",
            }
        )
        # Both MTO, so picking should be MTO
        self.assertEqual(self.picking.procure_method, "make_to_order")

        # Add one MTS move
        move3 = self.env["stock.move"].create(
            {
                "name": "TSTMOVE003",
                "picking_id": self.picking.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 30,
                "location_id": self.wh1.lot_stock_id.id,
                "location_dest_id": self.wh2.lot_stock_id.id,
                "procure_method": "make_to_stock",
            }
        )
        # Now mixed, should be False
        self.assertFalse(self.picking.procure_method)

        # Remove the MTS move
        move3.unlink()
        # Should be MTO again
        self.assertEqual(self.picking.procure_method, "make_to_order")

        # Remove one MTO move
        move2.unlink()
        # Still should be MTO
        self.assertEqual(self.picking.procure_method, "make_to_order")

        # Remove last move
        move1.unlink()
        # No moves, should be False
        self.assertFalse(self.picking.procure_method)

    def test_complex_mixed_scenarios(self):
        """Test various complex scenarios with multiple moves."""
        # Scenario 1: Three moves - 2 MTO, 1 MTS
        moves = []
        for i, method in enumerate(["make_to_order", "make_to_order", "make_to_stock"]):
            moves.append(
                self.env["stock.move"].create(
                    {
                        "name": f"TSTMOVE_S1_{i}",
                        "picking_id": self.picking.id,
                        "product_id": self.product.id,
                        "product_uom": self.product.uom_id.id,
                        "product_uom_qty": 10,
                        "location_id": self.wh1.lot_stock_id.id,
                        "location_dest_id": self.wh2.lot_stock_id.id,
                        "procure_method": method,
                    }
                )
            )
        self.assertFalse(self.picking.procure_method)

        # Clean up
        self.picking.move_ids.unlink()

        # Scenario 2: Four moves all MTS
        for i in range(4):
            self.env["stock.move"].create(
                {
                    "name": f"TSTMOVE_S2_{i}",
                    "picking_id": self.picking.id,
                    "product_id": self.product.id,
                    "product_uom": self.product.uom_id.id,
                    "product_uom_qty": 10,
                    "location_id": self.wh1.lot_stock_id.id,
                    "location_dest_id": self.wh2.lot_stock_id.id,
                    "procure_method": "make_to_stock",
                }
            )
        self.assertEqual(self.picking.procure_method, "make_to_stock")

    def test_inverse_procure_method_updates_all_moves(self):
        """Test that inverse updates all moves when procure_method is set."""
        # Create moves with different procure methods
        for i, method in enumerate(["make_to_stock", "make_to_order", "make_to_stock"]):
            self.env["stock.move"].create(
                {
                    "name": f"TSTMOVE_{i}",
                    "picking_id": self.picking.id,
                    "product_id": self.product.id,
                    "product_uom": self.product.uom_id.id,
                    "product_uom_qty": 10,
                    "location_id": self.wh1.lot_stock_id.id,
                    "location_dest_id": self.wh2.lot_stock_id.id,
                    "procure_method": method,
                }
            )

        # Verify mixed state
        self.assertFalse(self.picking.procure_method)
        self.assertEqual(len(self.picking.move_ids), 3)

        # Set all to MTO via picking
        self.picking.procure_method = "make_to_order"

        # All moves should now be MTO
        for move in self.picking.move_ids:
            self.assertEqual(move.procure_method, "make_to_order")

        # And picking should be MTO
        self.assertEqual(self.picking.procure_method, "make_to_order")
