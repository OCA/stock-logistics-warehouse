# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    allow_location_inconsistency = fields.Boolean(
        copy=False,
        help="If enabled, no error is raised for location inconsistency between "
        "picking and its move lines at the time of validation.",
    )

    def _get_child_location_ids(self, location):
        return self.env["stock.location"].search(
            [("id", "child_of", location.id), ("usage", "!=", "view")]
        )

    def _check_location_consistency(self, pick_location, line_locations):
        self.ensure_one()
        if not set(line_locations).issubset(
            self._get_child_location_ids(pick_location)
        ):
            raise UserError(
                _(
                    "A move line location is not related to that of the picking: %s",
                    self.name,
                )
            )

    def _action_done(self):
        for pick in self:
            if pick.allow_location_inconsistency:
                continue
            line_source_locations = [
                line.location_id
                for line in pick.move_line_ids
                if not getattr(line.move_id, "is_subcontract", False)
            ]
            pick._check_location_consistency(pick.location_id, line_source_locations)
            if pick._check_immediate():
                line_dest_locations = pick.move_line_ids.location_dest_id
            else:
                line_dest_locations = pick.move_line_ids.filtered(
                    lambda line: line.qty_done > 0
                ).mapped("location_dest_id")
            pick._check_location_consistency(pick.location_dest_id, line_dest_locations)
        return super()._action_done()
