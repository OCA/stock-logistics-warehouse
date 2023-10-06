# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    stock_reserve_substract_forecasted_quantity = fields.Boolean(
        string="Substract Forecasted Quantity?",
        default=True,
    )
