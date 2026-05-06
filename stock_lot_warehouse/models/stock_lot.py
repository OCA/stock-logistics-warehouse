# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    warehouse_id = fields.Many2one(related="location_id.warehouse_id")
