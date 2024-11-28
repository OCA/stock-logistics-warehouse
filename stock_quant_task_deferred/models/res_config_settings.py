# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    defer_quant_tasks = fields.Boolean(
        related="company_id.defer_quant_tasks",
        readonly=False,
    )
