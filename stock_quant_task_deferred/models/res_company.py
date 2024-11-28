# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    defer_quant_tasks = fields.Boolean(
        help="Check this if you want to defer stock quant deletions and merges."
    )
