# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    count_all_products = fields.Boolean(
        string="Count All Products",
        related="company_id.count_all_products",
        readonly=False,
    )
