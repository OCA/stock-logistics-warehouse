# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    vertical_lift_skipped = fields.Boolean(
        "Skipped in Vertical Lift?",
        help="If this flag is set, it means that when the move "
        "was being processed in the Vertical Lift, the operator decided to "
        "skip its processing.",
    )

    def _get_shuttles(self, location):
        self.ensure_one()
        # Reached the top of hierarchy without finding a shuttle
        if not location:
            return self.env["vertical.lift.shuttle"]
        # Found a location linked to a shuttle
        if shuttles := location.inverse_vertical_lift_shuttle_ids:
            return shuttles
        # Check the parent location
        return self._get_shuttles(location.location_id)

    def fetch_vertical_lift_tray_source(self):
        self.ensure_one()
        location = self.location_id

        # If shuttle is explicitly provided in context (e.g. from wizard confirm)
        if self.env.context.get("shuttle_id"):
            location.fetch_vertical_lift_tray()
            return {"type": "ir.actions.client", "tag": "soft_reload"}

        # Otherwise, check for a unique link
        shuttles = self._get_shuttles(location)
        if len(shuttles) == 1:
            # Pass the shuttle_id to the location method via context
            location.with_context(shuttle_id=shuttles.id).fetch_vertical_lift_tray()
            return {"type": "ir.actions.client", "tag": "soft_reload"}

        # If shared (len > 1) or no link (len == 0), open shuttle selector
        return self._open_shuttle_selector(location, "fetch_vertical_lift_tray_source")

    def fetch_vertical_lift_tray_dest(self):
        self.ensure_one()
        location = self.location_dest_id

        # If shuttle is explicitly provided in context (e.g. from wizard confirm)
        if self.env.context.get("shuttle_id"):
            location.fetch_vertical_lift_tray()
            return {"type": "ir.actions.client", "tag": "soft_reload"}

        # Otherwise, check for a unique link
        shuttles = self._get_shuttles(location)
        if len(shuttles) == 1:
            # Pass the shuttle_id to the location method via context
            location.with_context(shuttle_id=shuttles.id).fetch_vertical_lift_tray()
            return {"type": "ir.actions.client", "tag": "soft_reload"}

        # If shared (len > 1) or no link (len == 0), open shuttle selector
        return self._open_shuttle_selector(location, "fetch_vertical_lift_tray_dest")

    def _open_shuttle_selector(self, location, method_name):
        return {
            "name": self.env._("Select Shuttle for %s", location.name),
            "type": "ir.actions.act_window",
            "res_model": "vertical.lift.select.shuttle",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_location_id": location.id,
                "default_res_model": self._name,
                "default_res_id": self.id,
                "default_method_name": method_name,
            },
        }
