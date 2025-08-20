# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    type_group_reservation_rate = fields.Float(
        compute="_compute_type_group_reservation_rate",
        store=True,
        help="This is the reservation rate across all picking moves of the"
        "same picking type group and of the same procurement group for the same "
        "product.",
    )

    def _get_type_group_reservation_rate(self):
        """
        The reservation rate is the rate between demand quantity
        and the quantity reserved in move lines.
        """
        demand_quantity = sum(self.mapped("product_uom_qty"))
        if demand_quantity:
            return (sum(self.move_line_ids.mapped("quantity")) / demand_quantity) * 100
        return 0.0

    @api.depends("state", "move_line_ids.quantity")
    def _compute_type_group_reservation_rate(self):
        """
        We compute the 'group' reservation rate on the move
        for all moves in the same group for the same product.
        We don't take into account draft, done and cancelled moves
        but we don't care about the record state as it represents
        the rate based on other records values.
        """
        zero_moves = self.browse()
        hundred_rate_moves = self.browse()
        for move in self:
            moves_for_rate = move.group_id.stock_move_ids.filtered(
                lambda m, the_move=move: the_move.product_id == m.product_id
                and m.picking_type_id.picking_type_group_id
                == the_move.picking_type_id.picking_type_group_id
            )
            if moves_for_rate:
                new_rate = moves_for_rate._get_type_group_reservation_rate()
                if move.type_group_reservation_rate != new_rate:
                    # Avoid to set a value if not changed
                    if new_rate == 100.0:
                        hundred_rate_moves |= move
                    else:
                        if move.type_group_reservation_rate != new_rate:
                            move.type_group_reservation_rate = new_rate
            else:
                zero_moves |= move
        # Optimize the writes on all moves with 0 and 100 rates, writing
        # only if value is not already that one
        if zero_moves:
            zero_moves.filtered(
                lambda m: not m.type_group_reservation_rate
            ).type_group_reservation_rate = 0.0
        if hundred_rate_moves:
            hundred_rate_moves.filtered(
                lambda m: m.type_group_reservation_rate != 100.0
            ).type_group_reservation_rate = 100.0
