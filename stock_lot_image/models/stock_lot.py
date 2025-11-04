# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    image_ids = fields.One2many(
        string="Images",
        comodel_name="stock.lot.image",
        inverse_name="lot_id",
    )
