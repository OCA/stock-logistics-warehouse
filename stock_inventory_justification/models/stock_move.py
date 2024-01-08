# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    inventory_justification_ids = fields.Many2many(
        string="Justifications",
        help="Inventory justifications",
        comodel_name="stock.inventory.justification",
        relation="stock_move_inventory_justification_rel",
        column1="move_id",
        column2="justification_id",
        readonly=True,
    )
