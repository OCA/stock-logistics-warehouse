# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import create_index


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def init(self):
        # Speed up the search of move lines being picked from a location
        # (see stock.quant._get_current_move_lines). Same index as the one
        # created by stock_storage_type to avoid duplicates when both are
        # installed.
        create_index(
            self._cr,
            "stock_move_line_location_state_index",
            self._table,
            ["location_id", "state"],
            where="state IS NULL OR state NOT IN ('cancel', 'done')",
        )
