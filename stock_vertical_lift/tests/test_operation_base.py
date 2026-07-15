# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import mute_logger

from .common import VerticalLiftCase

SHUTTLE_LOGGER = "odoo.addons.stock_vertical_lift.models.vertical_lift_shuttle"


class TestVerticalLiftOperationBase(VerticalLiftCase):
    """Cover base / transfer abstract methods that aren't exercised by the
    mode-specific tests: onchange dispatch, switch_* delegation and the
    early-return guards on the action buttons.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_out = cls.env.ref(
            "stock_vertical_lift.stock_picking_out_demo_vertical_lift_1"
        )
        cls.out_move_line = cls.picking_out.move_line_ids[0]

    @mute_logger(SHUTTLE_LOGGER)
    def test_onchange(self):
        operation = self._open_screen("pick")
        # With _barcode_scanned: the override returns the current record values.
        result = operation.onchange(
            {"_barcode_scanned": "fake-barcode"},
            ["_barcode_scanned"],
            {},
        )
        self.assertIn("value", result)
        # Without _barcode_scanned: the guard takes the False branch and
        # delegates to super(), which is a no-op for an empty change set.
        result = operation.onchange({}, [], {})
        self.assertIsInstance(result, dict)

    @mute_logger(SHUTTLE_LOGGER)
    def test_operation_switch(self):
        operation = self._open_screen("pick")
        # Switch to PUT
        operation.switch_put()
        self.assertEqual(self.shuttle.mode, "put")
        # Switch to Inventory
        operation.switch_inventory()
        self.assertEqual(self.shuttle.mode, "inventory")
        # Switch to PICK
        operation.switch_pick()
        self.assertEqual(self.shuttle.mode, "pick")

    @mute_logger(SHUTTLE_LOGGER)
    def test_button_when_wrong_state(self):
        # The buttons must do nothing
        # if not in the correct state
        operation = self._open_screen("pick")
        self.assertNotIn(operation.state, ("save", "release"))
        previous_state = operation.state

        # button_save
        self.assertIsNone(operation.button_save())
        self.assertEqual(operation.state, previous_state)

        # button_release
        self.assertIsNone(operation.button_release())
        self.assertEqual(operation.state, previous_state)

        # button_save_and_release
        self.assertIsNone(operation.button_save_and_release())
        self.assertEqual(operation.state, previous_state)
