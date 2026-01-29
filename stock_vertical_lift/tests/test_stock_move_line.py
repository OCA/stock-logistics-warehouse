# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.stock_vertical_lift.tests.common import VerticalLiftCase


class TestStockMoveLine(VerticalLiftCase):
    def setUp(self):
        super().setUp()
        self.shuttle_2 = self.env.ref(
            "stock_vertical_lift.stock_vertical_lift_demo_shuttle_2"
        )
        # Configure "Shared Storage" scenario.
        # Update Shuttle 2 to point to the same storage location as Shuttle 1.
        self.shuttle_2.write(
            {
                "use_shared_storage_location": True,
                "shared_storage_location_id": self.shuttle.shared_storage_location_id.id,  # noqa: E501
            }
        )

        # Create a Stock Move Line moving goods between two ambiguous locations:
        # Source: location_1a (Tray 1A)
        # Dest: location_1b (Tray 1B)
        self.move_line = self.env["stock.move.line"].create(
            {
                "product_id": self.product_socks.id,
                "product_uom_id": self.product_socks.uom_id.id,
                "location_id": self.location_1a.id,
                "location_dest_id": self.location_1b.id,
                "quantity": 1,
                "company_id": self.env.company.id,
            }
        )

    def test_fetch_vertical_lift_tray_source(self):
        """Verify the wizard flow for fetching the Source location."""

        # Simulate the user clicking "Fetch Source" on the move line.
        # Since the source location is reachable by two shuttles, we expect
        # an action window (wizard) instead of a direct hardware command.
        action = self.move_line.fetch_vertical_lift_tray_source()

        # Check that the returned action is indeed the Shuttle Selector wizard.
        self.assertEqual(action.get("res_model"), "vertical.lift.select.shuttle")
        self.assertEqual(action.get("type"), "ir.actions.act_window")

        # Action must carry specific context data (i.e. method name).
        wizard_context = action.get("context", {})
        self.assertEqual(
            wizard_context.get("default_method_name"), "fetch_vertical_lift_tray_source"
        )

        # Initialize the wizard using the context provided by the action.
        # We simulate the user explicitly choosing "Shuttle 2"
        wizard = (
            self.env["vertical.lift.select.shuttle"]
            .with_context(**wizard_context)
            .create(
                {
                    "shuttle_id": self.shuttle_2.id,
                }
            )
        )

        # Confirm the wizard. This triggers the callback to the model.
        # We expect a "soft_reload" action.
        result = wizard.action_confirm()
        self.assertEqual(result.get("tag"), "soft_reload")
        self.assertEqual(result.get("type"), "ir.actions.client")

    def test_fetch_vertical_lift_tray_dest(self):
        """Verify the wizard flow for fetching the Destination location."""

        # Simulate the user clicking "Fetch Destination" on the move line.
        # Since the source location is reachable by two shuttles, we expect
        # an action window (wizard) instead of a direct hardware command.
        action = self.move_line.fetch_vertical_lift_tray_dest()

        # Check that the returned action is indeed the Shuttle Selector wizard.
        self.assertEqual(action.get("res_model"), "vertical.lift.select.shuttle")
        self.assertEqual(action.get("type"), "ir.actions.act_window")

        # Action must carry specific context data (i.e. method name).
        wizard_context = action.get("context", {})
        self.assertEqual(
            wizard_context.get("default_method_name"), "fetch_vertical_lift_tray_dest"
        )

        # Initialize the wizard using the context provided by the action.
        # We simulate the user explicitly choosing "Shuttle 1"
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
        # We expect a "soft_reload" action.
        result = wizard.action_confirm()
        self.assertEqual(result.get("tag"), "soft_reload")
        self.assertEqual(result.get("type"), "ir.actions.client")

    def test_fetch_tray_unique_shuttle(self):
        """Verify the flow when no ambiguity exists (Direct Link)."""

        # Remove the ambiguity by unlinking Shuttle 2 from the shared storage.
        # Tray 1B is reachable ONLY via Shuttle 1.
        self.shuttle_2.write(
            {
                "use_shared_storage_location": False,
                "shared_storage_location_id": False,
            }
        )

        # Simulate the user clicking "Fetch Destination".
        # Because there is only one valid shuttle linked to the destination,
        # the system should automatically detect it and perform the action
        # immediately, skipping the wizard entirely.
        result = self.move_line.fetch_vertical_lift_tray_dest()

        # We verify that we received a success signal directly and that the
        # system did not attempt to open the shuttle selector wizard.
        self.assertEqual(result.get("tag"), "soft_reload")
        self.assertNotEqual(result.get("res_model"), "vertical.lift.select.shuttle")
