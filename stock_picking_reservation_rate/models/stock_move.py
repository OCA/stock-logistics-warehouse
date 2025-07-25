# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools import float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    reservation_rate = fields.Float(
        compute="_compute_reservation_rate",
        store=True,
        help="This is the reservation rate for this stock move. This is "
        "not computed for moves that are not assigned, partially available or done",
    )

    def _get_reservation_rate(self):
        self.ensure_one()
        return (
            sum(line.quantity for line in self.move_line_ids) / self.product_uom_qty
        ) * 100

    @api.depends("state", "move_line_ids.quantity")
    def _compute_reservation_rate(self):
        zero_moves = self.browse()
        for move in self:
            if not move.product_uom_qty or move.state not in (
                "assigned",
                "partially_available",
                "done",
            ):
                zero_moves |= move
            else:
                move.reservation_rate = move._get_reservation_rate()
        if zero_moves:
            zero_moves.filtered(
                lambda m: not float_is_zero(
                    m.reservation_rate, precision_rounding=m.product_id.uom_id.rounding
                )
            ).reservation_rate = 0.0
