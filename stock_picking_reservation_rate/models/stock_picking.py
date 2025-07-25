# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    reservation_rate = fields.Float(
        compute="_compute_reservation_rate",
        store=True,
    )

    @api.depends("move_ids.reservation_rate")
    def _compute_reservation_rate(self):
        for picking in self:
            picking.reservation_rate = sum(
                move.reservation_rate for move in picking.move_ids
            ) / len(picking.move_ids)
