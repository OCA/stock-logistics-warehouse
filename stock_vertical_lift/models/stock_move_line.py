# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    vertical_lift_skipped_date = fields.Datetime(
        "Skipped in Vertical Lift on",
        help="When the operator decided to skip this move line while it was "
        "being processed in the Vertical Lift. Skipped lines are proposed "
        "again once the other lines are processed, oldest skip first.",
    )
    vertical_lift_skipped = fields.Boolean(
        "Skipped in Vertical Lift?",
        compute="_compute_vertical_lift_skipped",
        inverse="_inverse_vertical_lift_skipped",
        help="If this flag is set, it means that when the move "
        "was being processed in the Vertical Lift, the operator decided to "
        "skip its processing.",
    )

    @api.depends("vertical_lift_skipped_date")
    def _compute_vertical_lift_skipped(self):
        for line in self:
            line.vertical_lift_skipped = bool(line.vertical_lift_skipped_date)

    def _inverse_vertical_lift_skipped(self):
        now = fields.Datetime.now()
        for line in self:
            if line.vertical_lift_skipped:
                line.vertical_lift_skipped_date = line.vertical_lift_skipped_date or now
            else:
                line.vertical_lift_skipped_date = False

    def fetch_vertical_lift_tray_source(self):
        self.ensure_one()
        self.location_id.fetch_vertical_lift_tray()
        return {"type": "ir.actions.client", "tag": "soft_reload"}

    def fetch_vertical_lift_tray_dest(self):
        self.ensure_one()
        self.location_dest_id.fetch_vertical_lift_tray()
        return {"type": "ir.actions.client", "tag": "soft_reload"}
