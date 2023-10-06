# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_reserve_substract_forecasted_quantity = fields.Boolean(
        related="company_id.stock_reserve_substract_forecasted_quantity",
        readonly=False,
    )
