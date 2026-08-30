# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    type_group_reservation_rate = fields.Float(
        compute="_compute_type_group_reservation_rate",
        store=True,
        index=True,
        help="This is the reservation rate across all picking moves of the"
        "same picking type group and of the same procurement group.",
    )
    picking_type_group_id = fields.Many2one(
        comodel_name="stock.picking.type.group",
        related="picking_type_id.picking_type_group_id",
    )
    additional_type_group_reservation_rate = fields.Float(
        compute="_compute_additional_type_group_reservation_rate",
        store=True,
        index=True,
        help="This is the reservation rate across all picking moves of the"
        "same picking type group and of the same procurement group.",
    )
    additional_picking_type_group_id = fields.Many2one(
        comodel_name="stock.picking.type.group",
        related="picking_type_id.additional_picking_type_group_id",
    )

    # Add index as used in the depends
    group_id = fields.Many2one(
        index=True,
    )

    @api.depends("group_id.stock_move_ids.type_group_reservation_rate")
    def _compute_type_group_reservation_rate(self):
        self._set_type_group_reservation_rate()

    @api.depends("group_id.stock_move_ids.type_group_reservation_rate")
    def _compute_additional_type_group_reservation_rate(self):
        self._set_type_group_reservation_rate(
            "additional_picking_type_group_id",
            rate_field="additional_type_group_reservation_rate",
        )

    def _set_type_group_reservation_rate(
        self,
        type_group_field="picking_type_group_id",
        rate_field="type_group_reservation_rate",
    ):
        """ """
        zero_rate = self.browse()
        for picking in self:
            # We take all pickings in the same procurement group and in the same
            # picking type group
            pickings_for_rate = picking.group_id.stock_move_ids.picking_id.filtered(
                lambda p, pick=picking: p.state
                in ("confirmed", "assigned", "partially_available")
                and p.picking_type_id.picking_type_group_id == pick[type_group_field]
            )
            if not pickings_for_rate.move_ids:
                zero_rate |= picking
            else:
                rate = sum(
                    move.type_group_reservation_rate
                    for move in pickings_for_rate.move_ids
                ) / len(pickings_for_rate.move_ids)
                if picking.type_group_reservation_rate != rate:
                    picking[rate_field] = rate
        if zero_rate:
            zero_rate[rate_field] = 0.0
