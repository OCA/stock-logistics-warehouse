# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class VerticalLiftOperationPick(models.Model):
    _name = "vertical.lift.operation.pick"
    _inherit = "vertical.lift.operation.transfer"
    _description = "Vertical Lift Operation Pick"

    _initial_state = "noop"

    def _selection_states(self):
        return [
            ("noop", "No operations"),
            ("scan_destination", "Scan New Destination Location"),
            ("save", "Pick goods and save"),
            ("release", "Release"),
        ]

    def _transitions(self):
        return (
            self.Transition(
                "noop", "scan_destination", lambda self: self.select_next_move_line()
            ),
            self.Transition("scan_destination", "save"),
            self.Transition("save", "release", lambda self: self.process_current()),
            # go to scan_destination if we have lines in queue, otherwise, go to noop
            self.Transition(
                "release", "scan_destination", lambda self: self.select_next_move_line()
            ),
            self.Transition("release", "noop"),
        )

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        if not self.current_move_line_id or self.current_move_line_id.state == "done":
            return
        if self.step() == "scan_destination":
            location = self.env["stock.location"].search([("barcode", "=", barcode)])
            if location:
                self.location_dest_id = location
                self.next_step()
            else:
                self.env.user.notify_warning(
                    _("No location found for barcode {}").format(barcode)
                )

    def _domain_move_lines_to_do(self):
        domain = [
            ("state", "in", ("assigned", "partially_available")),
            ("location_id", "child_of", self.location_id.id),
        ]
        return domain

    def _domain_move_lines_to_do_all(self):
        shuttle_locations = self.env["stock.location"].search(
            [("vertical_lift_kind", "=", "view")]
        )
        domain = [
            ("state", "in", ("assigned", "partially_available")),
            ("location_id", "child_of", shuttle_locations.ids),
        ]
        return domain

    def fetch_tray(self):
        self.current_move_line_id.fetch_vertical_lift_tray_source()

    def select_next_move_line(self):
        self.ensure_one()
        next_move_line = self.env["stock.move.line"].search(
            self._domain_move_lines_to_do(), limit=1
        )
        self.current_move_line_id = next_move_line
        if next_move_line:
            self.fetch_tray()
            return True
        return False

    def button_release(self):
        """Release the operation, go to the next"""
        super().button_release()
        if self.step() == "noop":
            # we don't need to release (close) the tray until we have reached
            # the last line: the release is implicit when a next line is
            # fetched
            self.shuttle_id.release_vertical_lift_tray()
            # sorry not sorry
            return self._rainbow_man()
