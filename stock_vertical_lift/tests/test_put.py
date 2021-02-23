# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import VerticalLiftCase


class TestPut(VerticalLiftCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_in = cls.env.ref(
            "stock_vertical_lift.stock_picking_in_demo_vertical_lift_1"
        )
        cls.picking_in.action_confirm()
        cls.in_move_line = cls.picking_in.move_line_ids
        cls.in_move_line.location_dest_id = cls.shuttle.location_id

    def test_put_action_open_screen(self):
        self.shuttle.switch_put()
        action = self.shuttle.action_open_screen()
        operation = self.shuttle._operation_for_mode()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "vertical.lift.operation.put")
        self.assertEqual(action["res_id"], operation.id)

    def test_switch_put(self):
        self.shuttle.switch_put()
        self.assertEqual(self.shuttle.mode, "put")
        self.assertEqual(
            self.shuttle._operation_for_mode().current_move_line_id,
            self.env["stock.move.line"].browse(),
        )

    def test_put_count_move_lines(self):
        # If stock_picking_cancel_confirm is installed, we need to explicitly
        # confirm the cancellation.
        try:
            self.picking_in.cancel_confirm = True
        except AttributeError:
            pass
        self.picking_in.action_cancel()
        put1 = self._create_simple_picking_in(
            self.product_socks, 10, self.location_1a_x1y1
        )
        put1.action_confirm()
        put2 = self._create_simple_picking_in(
            self.product_recovery, 10, self.vertical_lift_loc
        )
        put2.action_confirm()
        put3 = self._create_simple_picking_in(
            self.product_recovery, 10, self.vertical_lift_loc
        )
        put3.action_confirm()
        operation = self._open_screen("put")
        shuttle2 = self.env.ref(
            "stock_vertical_lift.stock_vertical_lift_demo_shuttle_2"
        )
        operation2 = self._open_screen("put", shuttle=shuttle2)

        # we don't really care about the "number_of_ops" for the
        # put-away, as the move lines are supposed to have the whole
        # whole shuttle view as destination
        self.assertEqual(operation.number_of_ops, 1)
        self.assertEqual(operation.number_of_ops_all, 3)
        self.assertEqual(operation2.number_of_ops, 0)
        self.assertEqual(operation2.number_of_ops_all, 3)

    def test_transition_start(self):
        operation = self._open_screen("put")
        # we begin with an empty screen, user has to scan a package, product,
        # or lot
        self.assertEqual(operation.state, "scan_source")

    def test_transition_scan_source_to_scan_tray_type(self):
        operation = self._open_screen("put")
        self.assertEqual(operation.state, "scan_source")
        # wrong barcode, nothing happens
        operation.on_barcode_scanned("foo")
        self.assertEqual(operation.state, "scan_source")
        # product scanned, move to next step
        operation.on_barcode_scanned(self.product_socks.barcode)
        self.assertEqual(operation.state, "scan_tray_type")
        self.assertEqual(operation.current_move_line_id, self.in_move_line)

    def test_transition_scan_tray_type_to_save(self):
        operation = self._open_screen("put")
        # assume we already scanned the product
        operation.state = "scan_tray_type"
        operation.current_move_line_id = self.in_move_line
        # wrong barcode, nothing happens
        operation.on_barcode_scanned("foo")
        # tray type scanned, move to next step
        operation.on_barcode_scanned(self.location_1a.tray_type_id.code)
        self.assertEqual(operation.state, "save")
        # a cell has been set
        self.assertTrue(
            self.in_move_line.location_dest_id in self.location_1a.child_ids
        )

    def test_change_tray_type_on_save(self):
        operation = self._open_screen("put")
        move_line = self.in_move_line
        # assume we already scanned the product and the tray type
        # and the assigned location was location_1a_x1y1
        operation.current_move_line_id = move_line
        move_line.location_dest_id = self.location_1a_x1y1
        operation.state = "save"
        # we want to use another tray with a different type though,
        # so we scan again
        operation.on_barcode_scanned(self.location_1b.tray_type_id.code)
        self.assertTrue(
            self.in_move_line.location_dest_id
            in self.shuttle.location_id.child_ids.child_ids
        )
        # we are still in save
        self.assertEqual(operation.state, "save")
        # a cell has been set in the other tray
        self.assertTrue(move_line.location_dest_id in self.location_1b.child_ids)

    def test_transition_scan_tray_type_no_empty_cell(self):
        operation = self._open_screen("put")
        # assume we already scanned the product
        operation.state = "scan_tray_type"
        operation.current_move_line_id = self.in_move_line
        # create a tray type without location, which is the same as if all the
        # locations of a tray type were full
        new_tray_type = self.env["stock.location.tray.type"].create(
            {"name": "new tray type", "code": "test", "rows": 1, "cols": 1}
        )
        operation.on_barcode_scanned(new_tray_type.code)
        # should stay the same state
        self.assertEqual(operation.state, "scan_tray_type")
        # destination not changed
        self.assertEqual(self.in_move_line.location_dest_id, self.shuttle.location_id)

    def test_transition_save(self):
        operation = self._open_screen("put")
        # first steps of the workflow are done
        operation.current_move_line_id = self.in_move_line
        operation.current_move_line_id.location_dest_id = self.location_1a_x1y1
        operation.state = "save"
        qty_to_process = self.in_move_line.product_qty
        operation.button_save()
        self.assertEqual(self.in_move_line.state, "done")
        self.assertEqual(self.in_move_line.qty_done, qty_to_process)

    def test_transition_button_release(self):
        operation = self._open_screen("put")
        move_line = self.in_move_line
        # first steps of the workflow are done
        operation.current_move_line_id = move_line
        operation.current_move_line_id.location_dest_id = self.location_1a_x1y1
        # for the test, we'll consider our last line has been delivered
        move_line.qty_done = move_line.product_qty
        move_line.move_id._action_done()

        operation = self._open_screen("put")
        operation.button_release()
        self.assertEqual(operation.state, "scan_source")
        self.assertFalse(operation.current_move_line_id)
