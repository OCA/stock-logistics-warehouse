# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    lst_price = fields.Float(digits="Product Price", string="Sales Price")
