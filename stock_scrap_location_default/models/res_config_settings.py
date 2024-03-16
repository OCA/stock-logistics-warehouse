# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    scrap_default_location_id = fields.Many2one(
        comodel_name="stock.location",
        related="company_id.scrap_default_location_id",
        readonly=False,
    )
