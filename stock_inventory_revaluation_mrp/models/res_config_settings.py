# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    lock_cost_products = fields.Boolean(
        string="Lock Costs on Products",
        related="company_id.lock_cost_products",
        readonly=False,
    )

    no_of_bom_version = fields.Integer(
        "Number of retained cost roll versions",
        related="company_id.no_of_bom_version",
        readonly=False
    )
