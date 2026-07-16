# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.stock.models.stock_location import Location
from odoo.addons.stock.models.stock_picking import Picking
from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel,
)


class ReleaseChannelRestrictionError(ValidationError):
    def __init__(self, message):
        super().__init__(message)


class ReleaseChannelLocationPickingRestrictionError(ReleaseChannelRestrictionError):
    def __init__(
        self,
        picking: Picking,
        location: Location,
        incoming_channels: StockReleaseChannel,
        channel: StockReleaseChannel,
        env,
    ):
        self.env = env
        error_msg = _(
            "You cannot move picking (%(picking_name)s) products "
            "to %(location_name)s. "
            "That location already has pending outgoing moves for "
            "%(release_channel_name)s release channel "
            "and/or pending incoming moves for "
            "%(incoming_channel_names)s.",
            picking_name=picking.name,
            location_name=location.name,
            incoming_channel_names=", ".join(
                incoming_channel.name for incoming_channel in incoming_channels
            ),
            release_channel_name=(
                channel.name if channel else _("Undefined")
            ),  # Pending moves with no release channel can be contained in location
        )
        super().__init__(error_msg)


class ReleaseChannelLocationRestrictionError(ReleaseChannelRestrictionError):
    def __init__(
        self,
        location: Location,
        incoming_channels: StockReleaseChannel,
        channel: StockReleaseChannel,
        env,
    ):
        self.env = env
        error_msg = _(
            "The location %(location_name)s is already restricted to "
            "%(release_channel_name)s release channel "
            "and you try to modify it to "
            "%(incoming_channel_names)s.",
            location_name=location.name,
            incoming_channel_names=", ".join(
                incoming_channel.name for incoming_channel in incoming_channels
            ),
            release_channel_name=(
                channel.name if channel else _("Undefined")
            ),  # Pending moves with no release channel can be contained in location
        )
        super().__init__(error_msg)
