# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.fields import first

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
        compute="_compute_current_release_channel_restriction_id",
        recursive=True,
        store=True,
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
    release_channel_restriction_in_move = fields.Boolean(
        string="Release Channel Restriction For Incoming Moves",
        help=(
            "Check this box if you want to take into account all pending "
            "incoming movements to restrict the future movements to be "
            "in the same release channel."
        ),
    )

    def _get_first_ancestor_with_same_restriction(self):
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
        "location_id.release_channel_restriction",
        "release_channel_restriction",
        "pending_in_move_line_ids",
        "pending_out_move_line_ids",
        "location_id.current_release_channel_restriction_id",
    )
    def _compute_current_release_channel_restriction_id(self):
        """
        This will compute the current release channel that
        """
        locations_with_restriction = self.filtered(
            lambda location: location.release_channel_restriction == "same"
        )
        for location in locations_with_restriction:
            # Get all locations related to this one
            # (same parent with "same" restriction)
            parent = self._get_first_ancestor_with_same_restriction()
            family_location_ids = parent.child_ids
            release_channel_id = first(
                family_location_ids.pending_out_move_line_ids.picking_id.ship_picking_id.release_channel_id
            )

            location.current_release_channel_restriction_id = release_channel_id
        (
            self - locations_with_restriction
        ).current_release_channel_restriction_id = False

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
