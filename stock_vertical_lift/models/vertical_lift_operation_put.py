# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, models


class VerticalLiftOperationPut(models.Model):
    _name = "vertical.lift.operation.put"
    _inherit = "vertical.lift.operation.transfer"
    _description = "Vertical Lift Operation Put"

    def _domain_move_lines_to_do(self):
        # TODO check domain
        domain = [
            ("state", "=", "assigned"),
            ("location_dest_id", "child_of", self.location_id.id),
        ]
        return domain

    def _domain_move_lines_to_do_all(self):
        shuttle_locations = self.env["stock.location"].search(
            [("vertical_lift_kind", "=", "view")]
        )
        domain = [
            # TODO check state
            ("state", "=", "assigned"),
            ("location_dest_id", "child_of", shuttle_locations.ids),
        ]
        return domain

    def fetch_tray(self):
        self.current_move_line_id.fetch_vertical_lift_tray_dest()

    def process_current(self):
        raise exceptions.UserError(_("Put workflow not implemented"))
