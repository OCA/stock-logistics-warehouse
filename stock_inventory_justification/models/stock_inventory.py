# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    justification_ids = fields.Many2many(
        string="Justifications", comodel_name="stock.inventory.justification",
    )
