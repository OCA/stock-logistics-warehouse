# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    location_move = fields.Boolean(
        string="Part of move location",
        help="Whether this move is a part of stock_location moves",
    )

    @api.depends("location_move")
    def _compute_show_details_visible(self):
        super()._compute_show_details_visible()
        for move in self:
            move.show_details_visible = move.location_move
