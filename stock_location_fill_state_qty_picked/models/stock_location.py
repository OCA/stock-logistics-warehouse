# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    @property
    @api.model
    def _move_line_fill_state_qty_done(self):
        """
        Return the move line field that provides the quantity picked
        """
        return "qty_picked"

    @api.depends("pending_out_move_line_ids.qty_picked")
    def _compute_fill_state(self):
        return super()._compute_fill_state()
