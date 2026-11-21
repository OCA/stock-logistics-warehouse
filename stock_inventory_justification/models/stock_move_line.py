# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    inventory_justification_ids = fields.Many2many(
        string="Justifications",
        help="Inventory justifications",
        comodel_name="stock.inventory.justification",
        related="move_id.inventory_justification_ids",
        store=False,
        readonly=True,
    )
