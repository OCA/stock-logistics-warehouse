# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tools import mute_logger

from .common import VerticalLiftCase

SHUTTLE_LOGGER = "odoo.addons.stock_vertical_lift.models.vertical_lift_shuttle"


class TestVerticalLiftLocation(VerticalLiftCase):
    def test_vertical_lift_kind(self):
        # this boolean is what defines a "Vertical Lift View", the upper level
        # of the tree (View -> Shuttles -> Trays -> Cells)
        self.assertTrue(self.vertical_lift_loc.vertical_lift_location)
        self.assertEqual(self.vertical_lift_loc.vertical_lift_kind, "view")

        # check types accross the hierarchy
        shuttles = self.vertical_lift_loc.child_ids
        self.assertTrue(
            all(location.vertical_lift_kind == "shuttle" for location in shuttles)
        )
        trays = shuttles.mapped("child_ids")
        self.assertTrue(
            all(location.vertical_lift_kind == "tray" for location in trays)
        )
        cells = trays.mapped("child_ids")
        self.assertTrue(
            all(location.vertical_lift_kind == "cell" for location in cells)
        )

    @mute_logger(SHUTTLE_LOGGER)
    def test_fetch_vertical_lift_tray(self):
        shuttles = self.vertical_lift_loc.child_ids
        trays = shuttles.mapped("child_ids")
        cells = trays.mapped("child_ids")
        self.assertTrue(cells[0].button_fetch_vertical_lift_tray())
        message = "cell_location cannot be set when the location is a cell."
        with self.assertRaisesRegex(ValueError, message):
            cells[0].fetch_vertical_lift_tray(cells[0])
        message = "Cannot fetch a vertical lift tray on location"
        with self.assertRaisesRegex(exceptions.UserError, message):
            shuttles[0].fetch_vertical_lift_tray(cells[0])
        self.assertTrue(cells[0].button_release_vertical_lift_tray())

    def test_create_shuttle(self):
        # any location created directly under the view is a shuttle
        shuttle_loc = self.env["stock.location"].create(
            {
                "name": "Shuttle 42",
                "location_id": self.vertical_lift_loc.id,
                "usage": "internal",
            }
        )
        self.assertEqual(shuttle_loc.vertical_lift_kind, "shuttle")

    def test_fetch_vertical_lift_tray_ambiguous_error(self):
        # Configure "Shared Storage"
        shuttle_2 = self.env.ref(
            "stock_vertical_lift.stock_vertical_lift_demo_shuttle_2"
        )
        shuttle_2.write(
            {
                "use_shared_storage_location": True,
                "shared_storage_location_id": self.shuttle.shared_storage_location_id.id,  # noqa: E501
            }
        )

        # The system cannot decide between Shuttle 1 and Shuttle 2
        message = "Cannot determine which shuttle to use on location .*"
        with self.assertRaisesRegex(exceptions.UserError, message):
            self.location_1b.fetch_vertical_lift_tray()

    def test_button_fetch_vertical_lift_tray(self):
        # Configure "Shared Storage"
        # Shuttle 2 to point to the same storage location as Shuttle 1.
        shuttle_2 = self.env.ref(
            "stock_vertical_lift.stock_vertical_lift_demo_shuttle_2"
        )
        shuttle_2.write(
            {
                "use_shared_storage_location": True,
                "shared_storage_location_id": self.shuttle.shared_storage_location_id.id,  # noqa: E501
            }
        )

        # Simulate the user clicking "Fetch Shuttle Tray".
        # Since the tray is in shared storage, the system must prompt for a shuttle.
        action = self.location_1b.button_fetch_vertical_lift_tray()

        # Check that the returned action is the Shuttle Selector wizard.
        self.assertEqual(action.get("res_model"), "vertical.lift.select.shuttle")
        self.assertEqual(action.get("type"), "ir.actions.act_window")

        # Action must carry specific context data (i.e. method name).
        wizard_context = action.get("context", {})
        self.assertEqual(
            wizard_context.get("default_method_name"), "button_fetch_vertical_lift_tray"
        )

        # Initialize the wizard using the context provided by the action.
        # We simulate the user explicitly choosing "Shuttle 2".
        wizard = (
            self.env["vertical.lift.select.shuttle"]
            .with_context(**wizard_context)
            .create(
                {
                    "shuttle_id": shuttle_2.id,
                }
            )
        )

        # Confirm the wizard. This triggers the callback to the model.
        # The location button returns True upon successful execution.
        result = wizard.action_confirm()
        self.assertTrue(result)

    def test_button_fetch_vertical_lift_tray_no_wizard(self):
        # Simulate the user clicking "Fetch Tray".
        # Because there is only one valid shuttle, the system should perform
        # the action immediately, returning True instead of an action dict.
        result = self.location_1b.button_fetch_vertical_lift_tray()
        self.assertTrue(result)
        self.assertNotIsInstance(result, dict)

    def test_button_release_vertical_lift_tray(self):
        # Configure "Shared Storage":
        # Shuttle 2 to point to the same storage location as Shuttle 1.
        shuttle_2 = self.env.ref(
            "stock_vertical_lift.stock_vertical_lift_demo_shuttle_2"
        )
        shuttle_2.write(
            {
                "use_shared_storage_location": True,
                "shared_storage_location_id": self.shuttle.shared_storage_location_id.id,  # noqa: E501
            }
        )

        # Simulate the user clicking "Release Shuttle Tray".
        # Since the Tray 1B is in shared storage, the system must prompt for a shuttle.
        action = self.location_1b.button_release_vertical_lift_tray()

        # Check that the returned action is the Shuttle Selector wizard.
        self.assertEqual(action.get("res_model"), "vertical.lift.select.shuttle")
        self.assertEqual(action.get("type"), "ir.actions.act_window")

        # Action must carry specific context data (i.e. method name).
        wizard_context = action.get("context", {})
        self.assertEqual(
            wizard_context.get("default_method_name"),
            "button_release_vertical_lift_tray",
        )

        # Initialize the wizard using the context provided by the action.
        # We simulate the user explicitly choosing "Shuttle 1".
        wizard = (
            self.env["vertical.lift.select.shuttle"]
            .with_context(**wizard_context)
            .create(
                {
                    "shuttle_id": self.shuttle.id,
                }
            )
        )

        # Confirm the wizard. This triggers the callback to the model.
        # The location button returns True upon successful execution.
        result = wizard.action_confirm()
        self.assertTrue(result)

    def test_button_release_vertical_lift_tray_no_wizard(self):
        # Simulate the user clicking "Release Tray".
        # Should succeed immediately without a wizard.
        result = self.location_1b.button_release_vertical_lift_tray()
        self.assertTrue(result)
        self.assertNotIsInstance(result, dict)
