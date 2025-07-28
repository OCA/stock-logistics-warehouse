# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    type_group_reservation_rate = fields.Float(
        compute="_compute_type_group_reservation_rate",
        store=True,
        help="This is the reservation rate across all picking moves of the"
        "same picking type group and of the same procurement group.",
    )

    @api.depends("group_id.stock_move_ids.reservation_rate")
    def _compute_type_group_reservation_rate(self):
        zero_rate = self.browse()
        for picking in self:
            # We take all pickings in the same procurement group and in the same
            # picking type group
            pickings_for_rate = picking.group_id.stock_move_ids.picking_id.filtered(
                lambda p, pick=picking: p.state
                in ("confirmed", "assigned", "partially_available")
                and p.picking_type_id.picking_type_group_id
                == pick.picking_type_id.picking_type_group_id
            )
            if not pickings_for_rate.move_ids:
                zero_rate |= picking
            else:
                rate = sum(
                    move.reservation_rate for move in pickings_for_rate.move_ids
                ) / len(pickings_for_rate.move_ids)
                if picking.type_group_reservation_rate != rate:
                    picking.type_group_reservation_rate = rate
        if zero_rate:
            zero_rate.type_group_reservation_rate = 0.0
