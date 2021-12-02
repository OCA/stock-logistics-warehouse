# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import VerticalLiftCase


class TestPick(VerticalLiftCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_out = cls.env.ref(
            "stock_vertical_lift.stock_picking_out_demo_vertical_lift_1"
        )
        # we have a move line to pick created by demo picking
        # stock_picking_out_demo_vertical_lift_1
        cls.out_move_line = cls.picking_out.move_line_ids[0]

    def test_switch_pick(self):
        self.shuttle.switch_pick()
        self.assertEqual(self.shuttle.mode, "pick")
        self.assertEqual(
            self.shuttle._operation_for_mode().current_move_line_id, self.out_move_line
        )

    def test_pick_action_open_screen(self):
        self.shuttle.switch_pick()
        action = self.shuttle.action_open_screen()
        operation = self.shuttle._operation_for_mode()
        self.assertTrue(operation.current_move_line_id)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "vertical.lift.operation.pick")
        self.assertEqual(action["res_id"], operation.id)

    def test_pick_select_next_move_line(self):
        operation = self._open_screen("pick")
        operation.select_next_move_line()
        self.assertEqual(
            operation.current_move_line_id, self.picking_out.move_line_ids[1]
        )
        self.assertEqual(operation.state, "scan_destination")

    def test_pick_select_next_move_line_was_skipped(self):
        """Previously skipped moves can be reprocessed"""
        self.picking_out.move_line_ids.write({"vertical_lift_skipped": True})
        operation = self._open_screen("pick")
        self.assertEqual(
            operation.current_move_line_id, self.picking_out.move_line_ids[0]
        )
        operation.select_next_move_line()
        self.assertEqual(
            operation.current_move_line_id, self.picking_out.move_line_ids[1]
        )
        self.assertEqual(operation.state, "scan_destination")
        self.assertFalse(operation.current_move_line_id.vertical_lift_skipped)
        # When I skip the last move I come back to the first
        operation.select_next_move_line()
        self.assertEqual(
            operation.current_move_line_id, self.picking_out.move_line_ids[0]
        )

    def test_pick_save(self):
        operation = self._open_screen("pick")
        # assume we already scanned the destination, current state is save
        operation.state = "save"
        operation.current_move_line_id = self.out_move_line
        operation.button_save()
        self.assertEqual(operation.current_move_line_id.state, "done")
        self.assertEqual(operation.state, "release")

    def test_pick_skip_from_scan_destination(self):
        """Being in state Scan Destination, skip it"""
        self._test_pick_skip_from_state("scan_destination")

    def test_pick_skip_from_save(self):
        """Being in state Save, skip it"""
        self._test_pick_skip_from_state("save")

    def test_pick_skip_from_release(self):
        """Being in state Release, skip it"""
        self._test_pick_skip_from_state("release")

    def _test_pick_skip_from_state(self, state):
        operation = self._open_screen("pick")
        operation.state = state
        operation.current_move_line_id = self.out_move_line
        first_move_line = operation.current_move_line_id
        self.assertFalse(operation.current_move_line_id.vertical_lift_skipped)
        operation.button_skip()
        second_move_line = operation.current_move_line_id
        self.assertNotEqual(first_move_line, second_move_line)
        self.assertFalse(operation.current_move_line_id.vertical_lift_skipped)
        self.assertEqual(operation.current_move_line_id.state, "assigned")
        self.assertEqual(operation.state, "scan_destination")

    def test_pick_related_fields(self):
        operation = self._open_screen("pick")
        ml = operation.current_move_line_id = self.out_move_line

        # Trays related fields
        # For pick, this is the source location, which is the cell where the
        # product is.
        self.assertEqual(operation.tray_location_id, ml.location_id)
        self.assertEqual(
            operation.tray_name,
            # parent = tray
            ml.location_id.location_id.name,
        )
        self.assertEqual(
            operation.tray_type_id,
            # the tray type is on the parent of the cell (on the tray)
            ml.location_id.location_id.tray_type_id,
        )
        self.assertEqual(
            operation.tray_type_code, ml.location_id.location_id.tray_type_id.code
        )
        self.assertEqual(operation.tray_x, ml.location_id.posx)
        self.assertEqual(operation.tray_y, ml.location_id.posy)

        # Move line related fields
        self.assertEqual(operation.picking_id, ml.picking_id)
        self.assertEqual(operation.picking_origin, ml.picking_id.origin)
        self.assertEqual(operation.picking_partner_id, ml.picking_id.partner_id)
        self.assertEqual(operation.product_id, ml.product_id)
        self.assertEqual(operation.product_uom_id, ml.product_uom_id)
        self.assertEqual(operation.product_uom_qty, ml.product_uom_qty)
        self.assertEqual(operation.qty_done, ml.qty_done)
        self.assertEqual(operation.lot_id, ml.lot_id)

    def test_pick_count_move_lines(self):
        product1 = self.env.ref("stock_vertical_lift.product_running_socks")
        product2 = self.env.ref("stock_vertical_lift.product_recovery_socks")
        # cancel the picking from demo data to start from a clean state
        picking_1 = self.env.ref(
            "stock_vertical_lift.stock_picking_out_demo_vertical_lift_1"
        )
        # If stock_picking_cancel_confirm is installed, we need to explicitly
        # confirm the cancellation.
        try:
            picking_1.cancel_confirm = True
        except AttributeError:
            pass
        picking_1.action_cancel()

        # ensure that we have stock in some cells, we'll put product1
        # in the first Shuttle and product2 in the second
        cell1 = self.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_1a_x3y2"
        )
        self._update_quantity_in_cell(cell1, product1, 50)
        cell2 = self.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_2a_x1y1"
        )
        self._update_quantity_in_cell(cell2, product2, 50)

        # create pickings (we already have an existing one from demo data)
        pickings = self.env["stock.picking"].browse()
        pickings |= self._create_simple_picking_out(product1, 1)
        pickings |= self._create_simple_picking_out(product1, 1)
        pickings |= self._create_simple_picking_out(product1, 1)
        pickings |= self._create_simple_picking_out(product1, 1)
        pickings |= self._create_simple_picking_out(product2, 20)
        pickings |= self._create_simple_picking_out(product2, 30)
        # this one should be 'assigned', so should be included in the operation
        # count
        unassigned = self._create_simple_picking_out(product2, 1)
        pickings |= unassigned
        pickings.action_confirm()
        # product1 will be taken from the shuttle1, product2 from shuttle2
        pickings.action_assign()

        shuttle1 = self.shuttle
        operation1 = shuttle1._operation_for_mode()
        shuttle2 = self.env.ref(
            "stock_vertical_lift.stock_vertical_lift_demo_shuttle_2"
        )
        operation2 = shuttle2._operation_for_mode()

        self.assertEqual(operation1.number_of_ops, 4)
        self.assertEqual(operation2.number_of_ops, 2)
        self.assertEqual(operation1.number_of_ops_all, 6)
        self.assertEqual(operation2.number_of_ops_all, 6)

        # Process a line, should change the numbers.
        operation1.select_next_move_line()
        operation1.process_current()
        self.assertEqual(operation1.number_of_ops, 3)
        self.assertEqual(operation2.number_of_ops, 2)
        self.assertEqual(operation1.number_of_ops_all, 5)
        self.assertEqual(operation2.number_of_ops_all, 5)

        # add stock and make the last one assigned to check the number is
        # updated
        self._update_quantity_in_cell(cell2, product2, 10)
        unassigned.action_assign()
        self.assertEqual(operation1.number_of_ops, 3)
        self.assertEqual(operation2.number_of_ops, 3)
        self.assertEqual(operation1.number_of_ops_all, 6)
        self.assertEqual(operation2.number_of_ops_all, 6)

    def test_on_barcode_scanned(self):
        operation = self._open_screen("pick")
        self.assertEqual(operation.state, "scan_destination")
        # Scan wrong one first for test coverage
        operation.on_barcode_scanned("test")
        move_line = operation.current_move_line_id
        current_destination = move_line.location_dest_id
        stock_location = self.env.ref("stock.stock_location_stock")
        self.assertEqual(
            current_destination, self.env.ref("stock.stock_location_customers")
        )
        operation.on_barcode_scanned(stock_location.barcode)
        self.assertEqual(move_line.location_dest_id, stock_location)
        self.assertEqual(operation.state, "save")
        # Done for test coverage
        operation.button_save()
        operation.on_barcode_scanned("test")

    def test_button_release(self):
        self._open_screen("pick")
        self._test_button_release(self.picking_out.move_line_ids, "noop")

    def test_process_current_pick(self):
        operation = self._open_screen("pick")
        operation.current_move_line_id = self.out_move_line
        qty_to_process = self.out_move_line.product_qty
        operation.process_current()
        self.assertEqual(self.out_move_line.state, "done")
        self.assertEqual(self.out_move_line.qty_done, qty_to_process)

    def test_matrix(self):
        operation = self._open_screen("pick")
        operation.current_move_line_id = self.out_move_line
        location = self.out_move_line.location_id
        # offset by -1 because the fields are for humans
        expected_x = location.posx - 1
        expected_y = location.posy - 1
        self.assertEqual(
            operation.tray_matrix,
            {
                "selected": [expected_x, expected_y],
                # fmt: off
                'cells': [
                    [0, 0, 0, 0],
                    [1, 1, 1, 0],
                ]
                # fmt: on
            },
        )

    def test_tray_qty(self):
        cell = self.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_1a_x3y2"
        )
        self.out_move_line.location_id = cell
        operation = self.shuttle._operation_for_mode()
        operation.current_move_line_id = self.out_move_line
        self._update_quantity_in_cell(cell, self.out_move_line.product_id, 50)
        self.assertEqual(operation.tray_qty, 50)
        self._update_quantity_in_cell(cell, self.out_move_line.product_id, -20)
        self.assertEqual(operation.tray_qty, 30)
        self.assertTrue(operation.product_packagings)

    def test_product_packagings(self):
        operation = self.shuttle._operation_for_mode()
        ml = operation.current_move_line_id
        ml.move_id.state = "draft"
        ml.product_id = False
        self.assertFalse(operation.product_packagings)
