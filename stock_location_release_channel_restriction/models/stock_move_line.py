# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

from .exception import ReleaseChannelLocationRestrictionError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    for_restriction_incoming_location_channel_ids = fields.Many2many(
        compute="_compute_for_restriction_incoming_location_channel_ids",
        comodel_name="stock.release.channel",
        help="Technical field in order to retrieve the release channel of "
        "pending incoming moves on destination location.",
    )
    for_restriction_destination_location_channel_id = fields.Many2one(
        compute="_compute_for_restriction_destination_location_channel_id",
        comodel_name="stock.release.channel",
        help="Technical field in order to retrieve the release channel of pending moves"
        "on destination location.",
    )

    @api.depends(
        "location_dest_id.pending_in_move_line_ids.picking_id.release_channel_id"
    )
    def _compute_for_restriction_incoming_location_channel_ids(self):
        for line in self:
            line.for_restriction_incoming_location_channel_ids = line.location_dest_id.pending_in_move_line_ids.picking_id.release_channel_id  # noqa: E501

    @api.depends("location_dest_id.current_release_channel_restriction_id")
    def _compute_for_restriction_destination_location_channel_id(self):
        for line in self:
            line.for_restriction_destination_location_channel_id = (
                line.location_dest_id.current_release_channel_restriction_id
            )

    @property
    def _has_incoming_location_release_channel_restriction(self):
        """
        For better readability, this will check if incoming operations restriction
        is applicable
        """
        destination_channel = self.for_restriction_destination_location_channel_id
        in_channel = self.for_restriction_incoming_location_channel_ids
        return bool(
            self.location_dest_id.release_channel_restriction_in_move
            and (
                len(in_channel) > 1
                or (destination_channel and in_channel != destination_channel)
            )
        )

    @property
    def _has_destination_location_release_channel_restriction(self):
        """
        Check if the destination location has no pending moves
        with another release channel
        """
        self.ensure_one()
        # We are not sure existing pending moves are not in
        destination_channel = self.for_restriction_destination_location_channel_id
        return bool(
            self.location_dest_id.release_channel_restriction == "same"
            and (
                destination_channel
                and (self.picking_id.release_channel_id != destination_channel)
                or self._has_incoming_location_release_channel_restriction
            )
        )

    def _action_done(self):
        for line in self:
            if line._has_destination_location_release_channel_restriction:
                raise ReleaseChannelLocationRestrictionError(
                    line.picking_id,
                    line.location_dest_id,
                    line.for_restriction_incoming_location_channel_ids,
                    line.for_restriction_destination_location_channel_id,
                    line.env,
                )
        return super()._action_done()
