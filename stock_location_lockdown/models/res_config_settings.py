# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_lockdown_on_stocked_location = fields.Boolean(
        related="company_id.allow_lockdown_on_stocked_location",
        readonly=False,
    )
    block_location_on_inventory = fields.Boolean(
        related="company_id.block_location_on_inventory",
        readonly=False,
    )
