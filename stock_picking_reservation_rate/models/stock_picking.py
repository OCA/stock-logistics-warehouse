# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    reservation_rate = fields.Float(
        compute="_compute_reservation_rate",
        store=True,
    )

    def _get_reservation_rate(self):
        self.ensure_one()
        return sum(move.reservation_rate for move in self.move_ids) / len(self.move_ids)

    @api.depends("move_ids.reservation_rate")
    def _compute_reservation_rate(self):
        zero_pickings = self.browse()
        for picking in self:
            if not picking.move_ids:
                zero_pickings |= picking
            else:
                reservation_rate = picking._get_reservation_rate()
                if picking.reservation_rate != reservation_rate:
                    picking.reservation_rate = reservation_rate
        if zero_pickings:
            # Don't update records that have already 0.0 as value
            zero_pickings.filtered(
                lambda p: not p.reservation_rate
            ).reservation_rate = 0.0
