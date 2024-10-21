# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    stock_safe_scrap = fields.Boolean(
        string="Safe Scrap Operations",
        help="Check this if you want that scrap operations are authorized on locations"
        "where no picking operations are in progress.",
    )
