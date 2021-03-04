# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from itertools import cycle

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
            ("skip", "Skip"),  # Virtual state.
        ]

    def _transitions(self):
        return (
            self.Transition(
                "noop", "scan_destination", lambda self: self.select_next_move_line()
            ),
            self.Transition("scan_destination", "skip", lambda self: self.is_skipped()),
            self.Transition("scan_destination", "save"),
            self.Transition("save", "skip", lambda self: self.is_skipped()),
            self.Transition("save", "release", lambda self: self.process_current()),
            self.Transition("release", "skip", lambda self: self.is_skipped()),
            # go to scan_destination if we have lines in queue, otherwise, go to noop
            self.Transition(
                "release", "scan_destination", lambda self: self.select_next_move_line()
            ),
            self.Transition("release", "noop"),
            self.Transition(
                "skip",
                "scan_destination",
                lambda self: self.select_next_move_line(),
                direct_eval=True,
            ),
            self.Transition("skip", "noop", direct_eval=True),
        )

    def is_skipped(self):
        """Was the current stock.move.line marked as to be skipped?"""
        self.ensure_one()
        return self.current_move_line_id.vertical_lift_skipped

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

    def _get_next_move_line(self, order):
        def get_next(move_lines, current_move_line):
            if not move_lines:
                return False
            move_lines_cycle = cycle(move_lines)
            if not current_move_line or current_move_line not in move_lines:
                return next(move_lines_cycle)
            # Point to current_move_line and then return the next
            while next(move_lines_cycle) != current_move_line:
                continue
            return next(move_lines_cycle)

        move_lines = self.env["stock.move.line"].search(
            self._domain_move_lines_to_do(), order=order
        )
        return get_next(move_lines, self.current_move_line_id)

    def select_next_move_line(self):
        self.ensure_one()
        next_move_line_order = "vertical_lift_skipped"
        if self._order:
            # If there already exists an order, keep it.
            next_move_line_order += "," + self._order
        next_move_line = self._get_next_move_line(next_move_line_order)
        self.current_move_line_id = next_move_line
        if next_move_line:
            if next_move_line.vertical_lift_skipped:
                # If a move line that was previously skipped was selected,
                # we allow to process it again (maybe this time it's not
                # skipped).
                next_move_line.vertical_lift_skipped = False
            self.fetch_tray()
            return True
        return False

    def button_release(self):
        """Release the operation, go to the next"""
        res = super().button_release()
        if self.step() == "noop":
            # we don't need to release (close) the tray until we have reached
            # the last line: the release is implicit when a next line is
            # fetched
            self.shuttle_id.release_vertical_lift_tray()
            # sorry not sorry
            res = self._rainbow_man()
        return res

    def button_skip(self):
        """Skip the operation, go to the next"""
        self.ensure_one()
        self.current_move_line_id.vertical_lift_skipped = True
        if self.step() != "noop":
            self.next_step()
