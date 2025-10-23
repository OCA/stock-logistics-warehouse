# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo.tools import mute_logger

from .common import VerticalLiftCase

_logger = logging.getLogger(__name__)
SHUTTLE_LOGGER = "odoo.addons.stock_vertical_lift.models.vertical_lift_shuttle"


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

    @mute_logger(SHUTTLE_LOGGER)
    def test_put_action_open_screen(self):
        self.shuttle.switch_put()
        action = self.shuttle.action_open_screen()
        operation = self.shuttle._operation_for_mode()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "vertical.lift.operation.put")
        self.assertEqual(action["res_id"], operation.id)

    @mute_logger(SHUTTLE_LOGGER)
    def test_switch_put(self):
        self.shuttle.switch_put()
        self.assertEqual(self.shuttle.mode, "put")
        self.assertEqual(
            self.shuttle._operation_for_mode().current_move_line_id,
            self.env["stock.move.line"].browse(),
        )

    @mute_logger(SHUTTLE_LOGGER, "odoo.models.unlink")
    def test_put_count_move_lines(self):
        # If stock_picking_cancel_confirm is installed, we need to explicitly
        # confirm the cancellation.
        if hasattr(self.picking_in, "cancel_confirm"):
            self.picking_in.cancel_confirm = True
        else:
            _logger.debug(
                "stock_picking_cancel_confirm module is not installed - "
                "skipping cancel confirmation"
            )
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

    @mute_logger(SHUTTLE_LOGGER)
    def test_transition_start(self):
        operation = self._open_screen("put")
        # we begin with an empty screen, user has to scan a package, product,
        # or lot
        self.assertEqual(operation.state, "scan_source")

    @mute_logger(SHUTTLE_LOGGER)
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

    @mute_logger(SHUTTLE_LOGGER)
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

    @mute_logger(SHUTTLE_LOGGER)
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

    @mute_logger(SHUTTLE_LOGGER)
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

    @mute_logger(SHUTTLE_LOGGER)
    def test_transition_save(self):
        operation = self._open_screen("put")
        # first steps of the workflow are done
        operation.current_move_line_id = self.in_move_line
        operation.current_move_line_id.location_dest_id = self.location_1a_x1y1
        operation.state = "save"
        qty_to_process = self.in_move_line.quantity
        operation.button_save()
        self.assertEqual(self.in_move_line.state, "done")
        self.assertEqual(self.in_move_line.quantity, qty_to_process)

    @mute_logger(SHUTTLE_LOGGER)
    def test_transition_button_release(self):
        operation = self._open_screen("put")
        move_line = self.in_move_line
        # first steps of the workflow are done
        operation.current_move_line_id = move_line
        operation.current_move_line_id.location_dest_id = self.location_1a_x1y1
        # for the test, we'll consider our last line has been delivered
        move_line.move_id._action_done()

        operation = self._open_screen("put")
        operation.button_release()
        self.assertEqual(operation.state, "scan_source")
        self.assertFalse(operation.current_move_line_id)

    @mute_logger(SHUTTLE_LOGGER, "odoo.models.unlink")
    def test_put_package_with_multiple_move_lines(self):
        """Check moving a package linked to multiple move lines.

        Even when scanning a package, the module moves one move line at a time
        And not the whole package.
        If the package is spread on multiple move lines an exception is raised.

        The module will try to merge the move lines.

        """
        pick = self.picking_in
        # split the move in 2 move lines
        line1 = pick.move_line_ids
        # Add two quants in a package
        pack = self.env["stock.quant.package"].create({"name": "test"})
        # Update the available stock necessary for the move
        self._update_qty_in_location(pick.location_id, line1.product_id, 14, pack)
        # The stock for the 2nd move line must be on a different quant
        self.env["stock.quant"].create(
            {
                "product_id": line1.product_id.id,
                "location_id": pick.location_id.id,
                "quantity": 1,
                "package_id": pack.id,
            }
        )
        # Split the move line to have 2
        line2 = line1.copy({"quantity": 1, "picking_id": pick.id})
        line1.with_context(bypass_reservation_update=True).quantity = 14
        line1.package_id = pack
        line2.package_id = pack

        # Do the full put workflow
        operation = self._open_screen("put")
        line = operation._find_move_line(pack.name)
        operation.current_move_line_id = line
        operation.current_move_line_id.location_dest_id = self.location_1a_x1y1
        operation.state = "save"
        operation.button_save()
        self.assertEqual(line1.state, "done")
        # Check the lines quantity has been merged
        self.assertEqual(line1.quantity, 15)
        self.assertTrue(line1.picked)
        # Check there is no more move lines to do for the pack
        line_left = operation._find_move_line(pack.name)
        self.assertFalse(line_left)
        self.assertEqual(pick.state, "done")
