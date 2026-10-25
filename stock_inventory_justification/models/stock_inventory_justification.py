# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInventoryJustification(models.Model):
    _name = "stock.inventory.justification"
    _description = "Inventory justification"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

    _unique_name = models.Constraint(
        "EXCLUDE (name WITH =) WHERE (active = True)",
        "This stock inventory justification already exists.",
    )
