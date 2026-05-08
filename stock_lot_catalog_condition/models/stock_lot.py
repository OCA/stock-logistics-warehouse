# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    condition_color = fields.Integer(
        related="condition_id.color", string="Condition color"
    )
