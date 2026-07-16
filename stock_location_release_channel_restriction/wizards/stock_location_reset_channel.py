# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockLocationResetReleaseChannel(models.TransientModel):
    _name = "stock.location.reset.release.channel"
    _description = "Wizard to reset Release Channel on Locations"

    location_ids = fields.Many2many(
        comodel_name="stock.location",
    )
    reset_family = fields.Boolean(
        help="Check this in order to reset the blocking release channel on other "
        "locations from the same family."
    )

    def reset(self):
        for wizard in self:
            wizard.location_ids._remove_current_release_channel_restriction(
                force=True, family=wizard.reset_family
            )
