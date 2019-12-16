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
        cls.in_move_line.location_dest_id = cls.location_1a_x3y1

    def _select_move_lines(self, shuttle, move_lines=None):
        select_model = self.env["vertical.lift.operation.put.select"]
        operation = shuttle._operation_for_mode()
        select = select_model.create({"operation_id": operation.id})
        if move_lines:
            select.move_line_ids = [(6, 0, move_lines.ids)]
        else:
            select.action_add_all()
        select._sync_lines()

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

    def test_select_from_barcode(self):
        self.shuttle.switch_put()
        self.picking_in.action_cancel()
        put1 = self._create_simple_picking_in(
            self.product_socks, 10, self.location_1a_x1y1
        )
        put1.action_confirm()
        put2 = self._create_simple_picking_in(
            self.product_recovery, 10, self.location_1a_x2y1
        )
        put2.action_confirm()
        select_model = self.env["vertical.lift.operation.put.select"]
        operation = self.shuttle._operation_for_mode()
        select = select_model.create({"operation_id": operation.id})
        select.on_barcode_scanned(self.product_socks.barcode)
        self.assertRecordValues(select, [{"move_line_ids": put1.move_line_ids.ids}])
        select.on_barcode_scanned(self.product_recovery.barcode)
        self.assertRecordValues(
            select, [{"move_line_ids": (put1.move_line_ids | put2.move_line_ids).ids}]
        )
        select.action_validate()
        self.assertEqual(len(operation.operation_line_ids), 2)
        self.assertRecordValues(
            operation.mapped("operation_line_ids"),
            [
                {"move_line_id": put1.move_line_ids.id},
                {"move_line_id": put2.move_line_ids.id},
            ],
        )

    def test_no_select_from_barcode_outside_location(self):
        self.shuttle.switch_put()
        self.picking_in.action_cancel()
        location = self.env.ref("stock.location_refrigerator_small")
        put1 = self._create_simple_picking_in(self.product_socks, 10, location)
        put1.action_confirm()
        select_model = self.env["vertical.lift.operation.put.select"]
        operation = self.shuttle._operation_for_mode()
        select = select_model.create({"operation_id": operation.id})
        select.on_barcode_scanned(self.product_socks.barcode)
        # the move line is outside of the vertical lift, should not be
        # selected
        self.assertRecordValues(select, [{"move_line_ids": []}])

    def test_put_count_move_lines(self):
        self.shuttle.switch_put()
        self.picking_in.action_cancel()
        put1 = self._create_simple_picking_in(
            self.product_socks, 10, self.location_1a_x1y1
        )
        put1.action_confirm()
        put2 = self._create_simple_picking_in(
            self.product_recovery, 10, self.location_1a_x2y1
        )
        put2.action_confirm()
        put3 = self._create_simple_picking_in(
            self.product_recovery, 10, self.location_2a_x1y1
        )
        put3.action_confirm()
        operation = self.shuttle._operation_for_mode()
        self._select_move_lines(self.shuttle)
        shuttle2 = self.env.ref(
            "stock_vertical_lift.stock_vertical_lift_demo_shuttle_2"
        )
        shuttle2.switch_put()
        operation2 = shuttle2._operation_for_mode()
        self._select_move_lines(shuttle2)

        self.assertEqual(operation.number_of_ops, 2)
        self.assertEqual(operation.number_of_ops_all, 3)
        self.assertEqual(operation2.number_of_ops, 1)
        self.assertEqual(operation2.number_of_ops_all, 3)

    def test_process_current_put(self):
        self.shuttle.switch_put()
        operation = self.shuttle._operation_for_mode()
        self._select_move_lines(self.shuttle, self.in_move_line)
        self.assertEqual(operation.current_move_line_id, self.in_move_line)
        qty_to_process = self.in_move_line.product_qty
        operation.process_current()
        self.assertEqual(self.in_move_line.state, "done")
        self.assertEqual(self.in_move_line.qty_done, qty_to_process)

    def test_transition_reset(self):
        self.shuttle.switch_put()
        operation = self.shuttle._operation_for_mode()
        self._select_move_lines(self.shuttle, self.in_move_line)
        operation.state = "scan_tray_type"
        operation.reset_steps()
        self.assertEqual(operation.step(), "scan_product")

    def test_transition_scan_product(self):
        self.shuttle.switch_put()
        operation = self.shuttle._operation_for_mode()
        self._select_move_lines(self.shuttle, self.in_move_line)
        operation.state = "scan_product"
        # wrong barcode, nothing happens
        operation.on_barcode_scanned("foo")
        # product scanned, move to next step
        operation.on_barcode_scanned(self.product_socks.barcode)
        self.assertEqual(operation.step(), "scan_tray_type")

    def test_transition_scan_tray_type(self):
        self.shuttle.switch_put()
        operation = self.shuttle._operation_for_mode()
        self._select_move_lines(self.shuttle, self.in_move_line)
        operation.state = "scan_tray_type"
        # wrong barcode, nothing happens
        operation.on_barcode_scanned("foo")
        # tray type scanned, move to next step
        operation.on_barcode_scanned(operation.tray_type_id.code)
        self.assertEqual(operation.step(), "save")

    def test_transition_save(self):
        self.shuttle.switch_put()
        operation = self.shuttle._operation_for_mode()
        self._select_move_lines(self.shuttle, self.in_move_line)
        operation.state = "save"
        operation.button_save()
        self.assertEqual(operation.step(), "release")

    def test_transition_button_release(self):
        self.shuttle.switch_put()
        self._test_button_release(self.in_move_line)
