# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLotCondition(models.Model):
    _name = "stock.lot.condition"
    _description = "Stock Lot Condition"
    _order = "sequence, id"

    sequence = fields.Integer()
    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    description = fields.Char(translate=True)
    required_note = fields.Boolean(
        string="Required note?",
        help="If this box is checked, it will be mandatory to indicate a text for "
        "this condition in lots.",
    )
