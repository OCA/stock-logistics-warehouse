# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_quant_no_inventory_if_being_picked = fields.Boolean(
        related="company_id.stock_quant_no_inventory_if_being_picked", readonly=False
    )
