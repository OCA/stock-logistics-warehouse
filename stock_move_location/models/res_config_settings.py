# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    move_location_allow_immediate_transfer = fields.Boolean(
        related="company_id.move_location_allow_immediate_transfer", readonly=False
    )
