# © 2016 Numérigraphe SARL
# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_reserved_locations(self):
        self.ensure_one()
        return self.move_line_ids.mapped("location_id")

    def _get_dest_locations(self):
        self.ensure_one()
        return self.move_line_ids.mapped("location_dest_id")

    @api.constrains("location_dest_id", "location_id", "state")
    def _check_locked_location(self):
        for move_line in self.filtered(lambda m: m.state == "done"):
            locked_location_ids = self.env[
                "stock.inventory"
            ]._get_locations_open_inventories(
                [move_line.location_dest_id.id, move_line.location_id.id]
            )
            if locked_location_ids and not any(
                [
                    move_line.location_dest_id.usage == "inventory",
                    move_line.location_id.usage == "inventory",
                ]
            ):
                location_names = locked_location_ids.mapped("complete_name")
                raise ValidationError(
                    _(
                        "Inventory adjusment underway at "
                        "the following location(s):\n- %s\n"
                        "Moving products to or from these locations is "
                        "not allowed until the inventory adjustment is complete."
                    )
                    % "\n - ".join(location_names)
                )
