# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

from .exception import ReleaseChannelLocationPickingRestrictionError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    has_location_destination_release_channel_restriction = fields.Boolean(
        compute="_compute_has_location_destination_release_channel_restriction",
        help="This is used to easily check if the move line has a restriction "
        "for currrent destination location on release channel.",
    )

    @api.depends("location_dest_id.current_release_channel_restriction_id")
    def _compute_has_location_destination_release_channel_restriction(self):
        void_lines = self.browse()
        for line in self:
            if line.location_dest_id.release_channel_restriction != "same":
                void_lines |= line
                continue
            channel = line.picking_id.ship_picking_id.release_channel_id
            current_channel = (
                line.location_dest_id.current_release_channel_restriction_id
            )
            if current_channel and current_channel != channel:
                line.has_location_destination_release_channel_restriction = True
            else:
                void_lines |= line
        if void_lines:
            void_lines.has_location_destination_release_channel_restriction = False

    def _check_location_destination_release_channel_restriction(self) -> None:
        for line in self:
            if line.has_location_destination_release_channel_restriction:
                current_channel = (
                    line.location_dest_id.current_release_channel_restriction_id
                )
                raise ReleaseChannelLocationPickingRestrictionError(
                    line.picking_id,
                    line.location_dest_id,
                    line.location_dest_id.current_release_channel_restriction_id,
                    current_channel,
                    line.env,
                )

    def _valid_location_release_channel_restriction(self, location) -> bool:
        """
        Helper method to check if the location can be used as destination
        for the current moves.

        Return False if not a valid destination location for the line
        Returns True if valid destination location
        """
        self.ensure_one()
        if location.release_channel_restriction != "same":
            return True

        if (
            not location.current_release_channel_restriction_id
            or self.picking_id.ship_picking_id.release_channel_id
            == location.current_release_channel_restriction_id
        ):
            return True
        return False

    def _set_release_channel_current_restriction(self):
        """
        Set the release channel that restrict the destination locations
        Set it to the children too
        """
        moves_to_restrict = self.filtered(
            lambda line: line.location_dest_id.release_channel_restriction == "same"
        )
        for release_channel, moves in moves_to_restrict.partition(
            "picking_id.ship_picking_id.release_channel_id"
        ).items():
            moves._check_location_destination_release_channel_restriction()
            # Normal users could not have rights to write on locations
            moves.location_dest_id.sudo().write(
                {"current_release_channel_restriction_id": release_channel.id}
            )
            moves.location_dest_id._set_release_channel_restriction_family(
                release_channel
            )

    def _remove_release_channel_current_restriction(self, force=False):
        # Group the removal
        # Check if there is currently a release channel restriction
        for location, lines in (
            self.filtered("location_id.current_release_channel_restriction_id")
            .partition("location_id")
            .items()
        ):
            # Remove it if no family location has pending outgoing moves
            parent = location._get_first_ancestor_with_same_restriction()
            family_locations = parent.children_ids.filtered(
                lambda child: child.release_channel_restriction == "same"
            )
            if not (family_locations.pending_out_move_line_ids - lines) or force:
                location.current_release_channel_restriction_id = False
                family_locations.current_release_channel_restriction_id = False

    def _action_done(self):
        """
        Before setting lines as done, remove the release channel
        on source location if needed (if all pending moves are done).

        Then, set the release channel on destination location.
        """
        # Remove it if needed on location source
        self._remove_release_channel_current_restriction()
        # Set the release channel that restricts the locations if needed
        self._set_release_channel_current_restriction()
        return super()._action_done()
