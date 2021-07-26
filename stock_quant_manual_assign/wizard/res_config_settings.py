# Copyright 2021 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_quant_manual_assign_as_done = fields.Boolean(
        related="company_id.stock_quant_manual_assign_as_done", readonly=False
    )
