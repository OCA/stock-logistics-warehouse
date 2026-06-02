# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    dock_ids = fields.Many2many(
        comodel_name="stock.dock",
        string="Docks",
    )
