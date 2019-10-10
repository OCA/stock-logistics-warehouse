# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class VerticalLiftOperationPick(models.Model):
    _name = "vertical.lift.operation.pick"
    _inherit = "vertical.lift.operation.transfer"
    _description = "Vertical Lift Operation Pick"

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        location = self.env["stock.location"].search(
            [("barcode", "=", barcode)]
        )
        if location:
            self.current_move_line_id.location_dest_id = location
            self.operation_descr = _("Save")
        else:
            self.env.user.notify_warning(
                _("No location found for barcode {}").format(barcode)
            )

    def _domain_move_lines_to_do(self):
        # TODO check domain
        domain = [
            ("state", "=", "assigned"),
            ("location_id", "child_of", self.location_id.id),
        ]
        return domain

    def _domain_move_lines_to_do_all(self):
        shuttle_locations = self.env["stock.location"].search(
            [("vertical_lift_kind", "=", "view")]
        )
        # TODO check domain
        domain = [
            ("state", "=", "assigned"),
            ("location_id", "child_of", shuttle_locations.ids),
        ]
        return domain

    def fetch_tray(self):
        self.current_move_line_id.fetch_vertical_lift_tray_source()

    def process_current(self):
        # test code, TODO the smart one
        # (scan of barcode increments qty, save calls action_done?)
        line = self.current_move_line_id
        if line.state != "done":
            line.qty_done = line.product_qty
            line.move_id._action_done()

    def on_screen_open(self):
        """Called when the screen is open"""
        self.select_next_move_line()

    def select_next_move_line(self):
        self.ensure_one()
        next_move_line = self.env["stock.move.line"].search(
            self._domain_move_lines_to_do(), limit=1
        )
        self.current_move_line_id = next_move_line
        # TODO use a state machine to define next steps and
        # description?
        descr = (
            _("Scan New Destination Location")
            if next_move_line
            else _("No operations")
        )
        self.operation_descr = descr
        if next_move_line:
            self.fetch_tray()
