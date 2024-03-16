# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    scrap_default_location_id = fields.Many2one(
        comodel_name="stock.location",
        domain="[('scrap_location', '=', True), ('company_id', 'in', [company_id, False])]",
        check_company=True,
    )
