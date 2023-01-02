# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockInventoryReason(models.Model):
    _name = "stock.inventory.reason"
    _description = "Stock Inventory Reason"

    name = fields.Char(string="Reason Name")
    description = fields.Text(string="Reason Description")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "name_unique",
            "UNIQUE(name)",
            "You cannot have two reasons with the same name.",
        )
    ]
