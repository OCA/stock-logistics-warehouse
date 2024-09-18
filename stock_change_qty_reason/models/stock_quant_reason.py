# Copyright 2019-2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockQuantReason(models.Model):
    _name = "stock.quant.reason"
    _description = "Stock Quant Reason"

    name = fields.Char("Reason Name", required=True)
    description = fields.Text("Reason Description")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "name_unique",
            "UNIQUE(name)",
            "You cannot have two reason with the same name.",
        )
    ]
