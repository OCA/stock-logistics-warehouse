# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    vertical_lift_location = fields.Boolean(
        "Is a Vertical Lift View Location?",
        default=False,
        help="Check this box to use it as the view for Vertical Lift Shuttles.",
    )
    vertical_lift_kind = fields.Selection(
        selection=[
            ("view", "View"),
            ("shuttle", "Shuttle"),
            ("tray", "Tray"),
            ("cell", "Cell"),
        ],
        compute="_compute_vertical_lift_kind",
        store=True,
    )

    # This is a one2one in practice, but this one is not really interesting.
    # It's there only to be in the depends of 'vertical_lift_shuttle_id', which
    # give the unique shuttle for any location in the tree (whether it's a
    # shuttle, a tray or a cell)
    inverse_vertical_lift_shuttle_ids = fields.One2many(
        comodel_name="vertical.lift.shuttle", inverse_name="location_id", readonly=True
    )
    # compute the unique shuttle for any shuttle, tray or cell location, by
    # going through the parents
    vertical_lift_shuttle_id = fields.Many2one(
        comodel_name="vertical.lift.shuttle",
        compute="_compute_vertical_lift_shuttle_id",
        store=True,
    )

    @api.depends(
        "location_id", "location_id.vertical_lift_kind", "vertical_lift_location"
    )
    def _compute_vertical_lift_kind(self):
        tree = {"view": "shuttle", "shuttle": "tray", "tray": "cell"}
        for location in self:
            if location.vertical_lift_location:
                location.vertical_lift_kind = "view"
                continue
            kind = tree.get(location.location_id.vertical_lift_kind, False)
            location.vertical_lift_kind = kind

    @api.depends(
        "inverse_vertical_lift_shuttle_ids", "location_id.vertical_lift_shuttle_id"
    )
    def _compute_vertical_lift_shuttle_id(self):
        for location in self:
            if location.inverse_vertical_lift_shuttle_ids:
                # we have a unique constraint on the other side
                assert len(location.inverse_vertical_lift_shuttle_ids) == 1
                shuttle = location.inverse_vertical_lift_shuttle_ids
            else:
                shuttle = location.location_id.vertical_lift_shuttle_id
            location.vertical_lift_shuttle_id = shuttle

    def _hardware_vertical_lift_fetch_tray(self, cell_location=None):
        payload = self._hardware_vertical_lift_fetch_tray_payload(cell_location)
        return self.vertical_lift_shuttle_id._hardware_send_message(payload)

    def _hardware_vertical_lift_fetch_tray_payload(self, cell_location=None):
        """Prepare "fetch" message to be sent to the vertical lift hardware

        Private method, this is where the implementation actually happens.
        Addons can add their instructions based on the hardware used for
        this location.

        The hardware used for a location can be found in:

        ``self.vertical_lift_shuttle_id.hardware``

        Each addon can implement its own mechanism depending of this value
        and must call ``super``.

        The method must send the command to the vertical lift to fetch / open
        the tray. If a ``cell_location`` is passed and if the hardware supports
        a way to show a cell (such as a laser pointer), it should send this
        command as well.

        Useful information that could be needed for the drivers:

        * Any field of `self` (name, barcode, ...) which is the current tray.
        * Any field of `cell_location` (name, barcode, ...) which is the cell
          in the tray.
        * ``self.vertical_lift_shuttle_id`` is the current Shuttle, where we
          find details about the hardware, the current mode (pick, put, ...).
        * ``self.tray_type_id`` is the kind of tray.
        * ``self.tray_type_id.width_per_cell`` and
          ``self.tray_type_id.depth_per_cell`` return the size of a cell in mm.
        * ``cell_location.posx`` and ``posy`` are the coordinate from the
          bottom-left of the tray.
        * ``cell_location.tray_cell_center_position()`` returns the central
          position of the cell in mm from the bottom-left of a tray. (distance
          from left, distance from bottom). Can be used for instance for
          highlighting the cell using a laser pointer.

        Returns a message in bytes, that will be sent through
        ``VerticalLiftShuttle._hardware_send_message()``.
        """
        if self.vertical_lift_shuttle_id.hardware == "simulation":
            message = _("Opening tray {}.").format(self.name)
            if cell_location:
                from_left, from_bottom = cell_location.tray_cell_center_position()
                message += _("<br/>Laser pointer on x{} y{} ({}mm, {}mm)").format(
                    cell_location.posx, cell_location.posy, from_left, from_bottom
                )
            return message.encode("utf-8")
        else:
            raise NotImplementedError()

    def fetch_vertical_lift_tray(self, cell_location=None):
        """Send instructions to the vertical lift hardware to fetch a tray

        Public method to use for:
        * fetch the vertical lift tray and presenting it to the operator
          (physically)
        * direct the laser pointer to the cell's location if set

        Depending on the hardware, the laser pointer may not be implemented.

        The actual implementation of the method goes in the private method
        ``_hardware_vertical_lift_fetch_tray()``.
        """
        self.ensure_one()
        if self.vertical_lift_kind == "cell":
            if cell_location:
                raise ValueError(
                    "cell_location cannot be set when the location is a cell."
                )
            tray = self.location_id
            tray.fetch_vertical_lift_tray(cell_location=self)
        elif self.vertical_lift_kind == "tray":
            self._hardware_vertical_lift_fetch_tray(cell_location=cell_location)
        else:
            raise exceptions.UserError(
                _("Cannot fetch a vertical lift tray on location %s") % (self.name,)
            )
        return True

    def button_fetch_vertical_lift_tray(self):
        self.ensure_one()
        if self.vertical_lift_kind in ("cell", "tray"):
            self.fetch_vertical_lift_tray()
        return True

    def button_release_vertical_lift_tray(self):
        self.ensure_one()
        if self.vertical_lift_kind:
            self.vertical_lift_shuttle_id.release_vertical_lift_tray()
        return True
