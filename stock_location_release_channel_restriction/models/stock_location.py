# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.fields import Command

from odoo.addons.stock.models.stock_move_line import StockMoveLine
from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel,
)

from .exception import ReleaseChannelLocationRestrictionError

RELEASE_RESTRICTION = [
    (
        "mixed",
        "Movements of different release channels are allowed into the location",
    ),
    (
        "same",
        "Only movements of the same release channel are allowed into the location",
    ),
]


class StockLocation(models.Model):
    _inherit = "stock.location"

    current_release_channel_restriction_id = fields.Many2one(
        comodel_name="stock.release.channel",
        readonly=True,
        help="This is the current release channel that restrict this "
        "location for future incoming movements.",
    )

    release_channel_restriction = fields.Selection(
        selection=RELEASE_RESTRICTION,
        help="If 'same' is selected the system will prevent to put "
        "items of different release channels into the same location.",
        compute="_compute_release_channel_restriction",
        store=True,
        recursive=True,
    )

    parent_release_channel_restriction = fields.Selection(
        string="Parent Location Release Channel Restriction",
        store=True,
        readonly=True,
        related="location_id.release_channel_restriction",
        recursive=True,
        help="This field is used to compute recursively the restriction parameter"
        " from parent hierarchy.",
    )

    specific_release_channel_restriction = fields.Selection(
        selection=RELEASE_RESTRICTION,
        default=False,
        help="If specified the restriction specified will apply to "
        "the current location and all its children",
    )

    def _set_release_channel_restriction_family(
        self, release_channel: StockReleaseChannel
    ):
        for location in self:
            parent = location._get_first_ancestor_with_same_channel_restriction()
            parent.children_ids.filtered(
                lambda child: child.release_channel_restriction == "same"
            ).sudo().write(
                {
                    "current_release_channel_restriction_id": release_channel.id,
                }
            )

    def _get_first_ancestor_with_same_channel_restriction(self):
        """
        This will retrieve all first parent with "same" restriction
        on the recordset.
        """
        self.ensure_one()
        location = self
        while parent := location.location_id:
            if (
                parent.release_channel_restriction == "same"
                and parent.location_id.release_channel_restriction != "same"
            ):
                return parent
            location = parent
        return self.browse()

    @api.depends(
        "specific_release_channel_restriction", "parent_release_channel_restriction"
    )
    def _compute_release_channel_restriction(self):
        default_value = "mixed"
        for rec in self:
            rec.release_channel_restriction = (
                rec.specific_release_channel_restriction
                or rec.parent_release_channel_restriction
                or default_value
            )

    def write(self, vals):
        if "current_release_channel_restriction_id" in vals and bool(
            vals.get("current_release_channel_restriction_id")
        ):
            channel = self.env["stock.release.channel"].browse(
                vals.get("current_release_channel_restriction_id")
            )
            self._check_current_release_channel_restriction(channel)
        return super().write(vals)

    def _check_current_release_channel_restriction(self, release_channel):
        locations_to_check = self.filtered(
            lambda location: location.release_channel_restriction == "same"
            and location.current_release_channel_restriction_id
        )
        for location in locations_to_check:
            if location.current_release_channel_restriction_id != release_channel:
                raise ReleaseChannelLocationRestrictionError(
                    location=location,
                    channel=location.current_release_channel_restriction_id,
                    incoming_channels=release_channel,
                    env=self.env,
                )

    def _remove_current_release_channel_restriction(
        self, lines: StockMoveLine | None = None, force=False, family=True
    ):
        """
            This will remove the current release channel restriction on locations.

        Args:
            lines (_type_, optional): The stock move lines to not take into account.
            force (bool, optional): Force the removal on self recordset.
            family (bool, optional): Remove the release channel on family locations too.
        """
        if lines is None:
            lines = self.env["stock.move.line"].browse()
        for location in self:
            # Remove it if no family location has pending outgoing moves
            parent = location._get_first_ancestor_with_same_channel_restriction()
            if family:
                family_locations = parent.children_ids.filtered(
                    lambda child: child.release_channel_restriction == "same"
                )
            else:
                family_locations = self.browse()
            locations = family_locations | location
            if not (locations.pending_out_move_line_ids - lines) or force:
                # users may not have write access on locations
                locations.sudo().current_release_channel_restriction_id = False

    def action_reset_release_channel(self):
        view_id = self.env.ref(
            "stock_location_release_channel_restriction.stock_location_reset_release_channel_form_view"
        ).id
        return {
            "name": _("Reset Release Channel"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock.location.reset.release.channel",
            "view_id": view_id,
            "views": [(view_id, "form")],
            "target": "new",
            "context": {
                "default_location_ids": [Command.set(self.ids)],
            },
        }
