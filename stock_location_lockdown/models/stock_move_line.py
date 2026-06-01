# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.constrains("location_id", "location_dest_id", "state")
    def _check_blocked_location(self):
        for line in self.filtered(lambda m: m.state == "done"):
            if line.location_id.is_outbound_blocked:
                raise ValidationError(
                    self.env._(
                        "The location %(location)s is blocked for outbound and "
                        "stock cannot be moved out of it.",
                        location=line.location_id.display_name,
                    )
                )
            if line.location_dest_id.is_inbound_blocked:
                raise ValidationError(
                    self.env._(
                        "The location %(location)s is blocked for inbound and "
                        "stock cannot be moved into it.",
                        location=line.location_dest_id.display_name,
                    )
                )
