# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    stock_safe_scrap = fields.Boolean(
        related="company_id.stock_safe_scrap",
        readonly=False,
    )
