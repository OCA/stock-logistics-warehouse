# Copyright 2019 Camptocamp SA
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import RecordCapturer
from odoo.tools import mute_logger

from .common import VerticalLiftCase

SHUTTLE_LOGGER = "odoo.addons.stock_vertical_lift.models.vertical_lift_shuttle"


class TestInventory(VerticalLiftCase):
    @mute_logger(SHUTTLE_LOGGER)
    def test_switch_inventory(self):
        self.shuttle.switch_inventory()
        self.assertEqual(self.shuttle.mode, "inventory")
        self.assertEqual(
            self.shuttle._operation_for_mode().quant_id,
            self.env["stock.quant"].browse(),
        )

    @mute_logger(SHUTTLE_LOGGER)
    def test_inventory_action_open_screen(self):
        self.shuttle.switch_inventory()
        action = self.shuttle.action_open_screen()
        operation = self.shuttle._operation_for_mode()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "vertical.lift.operation.inventory")
        self.assertEqual(action["res_id"], operation.id)

    @mute_logger(SHUTTLE_LOGGER)
    def test_inventory_actions(self):
        self.shuttle.switch_inventory()
        action = self.shuttle.action_menu()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "vertical.lift.shuttle")
        self.assertEqual(action["res_id"], self.shuttle.id)

        action = self.shuttle.action_back_to_settings()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "vertical.lift.shuttle")
        self.assertEqual(action["res_id"], 0)

        action = self.shuttle.action_manual_barcode()
        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["tag"], "vertical_lift_manual_barcode")
        self.assertEqual(action["name"], "Barcode")

    @mute_logger(SHUTTLE_LOGGER)
    def test_scheduled_count_without_value_is_queued(self):
        # A count scheduled with "Leave Empty" has no inventory quantity set yet
        # but must still show up in the queue (the bug this fixes).
        stock_quant = self._create_stock_quants(
            [(self.location_1a_x1y1, self.product_socks)]
        )[0]
        self.assertFalse(stock_quant.inventory_quantity_set)
        operation = self._open_screen("inventory")
        self.assertEqual(operation.number_of_ops, 1)
        self.assertEqual(operation.quant_id, stock_quant)

    @mute_logger(SHUTTLE_LOGGER)
    def test_set_value_scheduled_later_is_not_queued(self):
        # A count scheduled for a later date must NOT be queued yet, even when
        # its value is already set: `inventory_quantity_set` is no longer a
        # criteria, only the scheduled date is.
        stock_quant = self.env["stock.quant"].create(
            {
                "product_id": self.product_socks.id,
                "location_id": self.location_1a_x1y1.id,
                "product_uom_id": self.product_socks.uom_id.id,
            }
        )
        stock_quant.action_set_inventory_quantity()
        tomorrow = fields.Date.add(fields.Date.context_today(stock_quant), days=1)
        stock_quant.with_context(inventory_mode=True).write(
            {"inventory_date": tomorrow}
        )
        self.assertTrue(stock_quant.inventory_quantity_set)
        operation = self._open_screen("inventory")
        self.assertEqual(operation.number_of_ops, 0)
        self.assertFalse(operation.quant_id)

    @mute_logger(SHUTTLE_LOGGER)
    def test_reschedule_requeues_done_quant(self):
        # Once counted on the shuttle a quant is flagged done; rescheduling a new
        # count must clear that flag so it is queued again.
        stock_quant = self._create_stock_quants(
            [(self.location_1a_x1y1, self.product_socks)]
        )[0]
        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        operation = self._open_screen("inventory")
        operation.quantity_input = 10.0
        operation.button_save()
        self.assertTrue(stock_quant.vertical_lift_done)

        # schedule a new count
        stock_quant.with_context(inventory_mode=True).write(
            {"inventory_date": fields.Date.context_today(stock_quant)}
        )
        self.assertFalse(stock_quant.vertical_lift_done)
        operation = self._open_screen("inventory")
        self.assertEqual(operation.quant_id, stock_quant)

    @mute_logger(SHUTTLE_LOGGER)
    def test_inventory_count_ops(self):
        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        self._update_qty_in_location(self.location_1a_x2y1, self.product_recovery, 10)
        self._create_stock_quants(
            [
                (self.location_1a_x1y1, self.product_socks),
                (self.location_1a_x2y1, self.product_recovery),
            ]
        )
        self._update_qty_in_location(self.location_2a_x1y1, self.product_socks, 10)
        self._create_stock_quants([(self.location_2a_x1y1, self.product_socks)])

        operation = self._open_screen("inventory")
        self.assertEqual(operation.number_of_ops, 2)
        self.assertEqual(operation.number_of_ops_all, 3)

    @mute_logger(SHUTTLE_LOGGER)
    def test_process_current_inventory(self):
        stock_quant = self._create_stock_quants(
            [(self.location_1a_x1y1, self.product_socks)]
        )[0]
        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        operation = self._open_screen("inventory")
        self.assertEqual(operation.state, "quantity")
        self.assertEqual(operation.quant_id, stock_quant)
        # test the happy path, quantity is correct
        operation.quantity_input = 10.0
        result = operation.button_save()
        # state is reset
        # noop because we have no further lines
        self.assertEqual(operation.state, "noop")
        self.assertFalse(operation.quant_id)
        self.assertTrue(stock_quant.vertical_lift_done)
        expected_result = {
            "effect": {
                "fadeout": "slow",
                "message": self.env._("Congrats, you cleared the queue!"),
                "img_url": "/web/static/src/img/smile.svg",
                "type": "rainbow_man",
            }
        }
        self.assertEqual(result, expected_result)

    @mute_logger(SHUTTLE_LOGGER)
    def test_wrong_quantity(self):
        quant = self._create_stock_quants(
            [(self.location_1a_x1y1, self.product_socks)]
        )[0]
        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        operation = self._open_screen("inventory")
        stock_quant = operation.quant_id
        self.assertEqual(stock_quant, quant)

        operation.quantity_input = 12.0
        operation.button_save()
        self.assertEqual(operation.last_quantity_input, 12.0)
        self.assertEqual(operation.quantity_input, 0.0)
        self.assertEqual(operation.state, "confirm_wrong_quantity")
        self.assertEqual(operation.quant_id, stock_quant)

        # entering the same quantity a second time validates
        operation.quantity_input = 12.0
        with RecordCapturer(self.env["stock.move"], []) as capt:
            operation.button_save()
            move = capt.records[0]
            self.assertEqual(move.state, "done")
            self.assertEqual(move.quantity, 2.0)
        self.assertFalse(operation.quant_id)
        # applying the count reschedules the quant to a future date, which
        # clears the done marker (new count campaign)
        self.assertFalse(quant.vertical_lift_done)
        self.assertEqual(quant.quantity, 12.0)
        self.assertFalse(operation.quant_id)

    @mute_logger(SHUTTLE_LOGGER)
    def test_confirm_wrong_quantity(self):
        stock_quant = self._create_stock_quants(
            [(self.location_1a_x1y1, self.product_socks)]
        )[0]
        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        operation = self._open_screen("inventory")
        current_quant = operation.quant_id
        self.assertEqual(current_quant, stock_quant)

        operation.quantity_input = 12.0
        operation.button_save()
        self.assertEqual(operation.last_quantity_input, 12.0)
        self.assertEqual(operation.quantity_input, 0.0)
        self.assertEqual(operation.state, "confirm_wrong_quantity")
        self.assertEqual(operation.quant_id, current_quant)
        operation.button_save()
        self.assertEqual(operation.state, "quantity")

    @mute_logger(SHUTTLE_LOGGER)
    def test_inventory_next_line(self):
        stock_quants = self._create_stock_quants(
            [
                (self.location_1a_x1y1, self.product_socks),
                (self.location_1a_x2y1, self.product_recovery),
            ]
        )
        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        self._update_qty_in_location(self.location_1a_x2y1, self.product_recovery, 10)
        operation = self._open_screen("inventory")
        operation.quantity_input = 10.0
        result = operation.button_save()
        # no rainbow because still exist operation in queue
        self.assertFalse(result)
        #
        # go to next quant
        remaining_quant = stock_quants[1]
        self.assertEqual(operation.state, "quantity")
        self.assertEqual(operation.quant_id, remaining_quant)
        self.assertEqual(operation.last_quantity_input, 0.0)
        self.assertEqual(operation.quantity_input, 0.0)

    @mute_logger(SHUTTLE_LOGGER)
    def test_inventory_locations(self):
        self.shuttle.switch_inventory()
        opr_inventory = self.shuttle._operation_for_mode()
        opr_inventory._compute_tray_data()
        opr_inventory._compute_product_packagings()
        self.assertEqual(opr_inventory.product_packagings, "")
        opr_inventory._compute_tray_qty()
        self.assertEqual(opr_inventory.tray_qty, 0.0)

        self._update_qty_in_location(self.location_1a_x1y1, self.product_socks, 10)
        self._create_stock_quants([(self.location_1a_x1y1, self.product_socks)])
        self._open_screen("inventory")
        opr_inventory._compute_product_packagings()
        opr_inventory._compute_tray_qty()
        self.assertEqual(opr_inventory.tray_qty, 10)
