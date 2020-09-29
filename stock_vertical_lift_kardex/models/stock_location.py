# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, exceptions, models

_logger = logging.getLogger(__name__)


class StockLocation(models.Model):
    _inherit = "stock.location"

    def _hardware_kardex_prepare_fetch_payload(self, cell_location=None):
        if self.level is False:
            raise exceptions.UserError(
                _("Shuttle tray %s has no level. " "Please fix the configuration")
                % self.display_name
            )
        shuttle = self.vertical_lift_shuttle_id
        if cell_location:
            x, y = cell_location.tray_cell_center_position()
            if x == 0 and y == 0:
                raise exceptions.UserError(
                    _(
                        "Cell location %s has no position. "
                        "Check if the dimensions of tray %s "
                        "are properly set in the tray type."
                    )
                    % (cell_location.display_name, self.name)
                )
            x, y = int(x), int(y)
        else:
            x, y = "", ""
        subst = {
            "code": shuttle._kardex_shuttle_code(),
            "hostId": self.env["ir.sequence"].next_by_code("vertical.lift.command"),
            # hard code the gate for now.
            # TODO proper handling of multiple gates for 1 lift.
            "addr": shuttle.name + "-1",
            "carrier": self.level,
            "carrierNext": "0",
            "x": x,
            "y": y,
            "boxType": "",
            "Q": "",
            "order": "",
            "part": "",
            "desc": "",
        }
        return shuttle._hardware_kardex_format_template(subst)

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
        """
        if self.vertical_lift_shuttle_id.hardware == "kardex":
            payload = self._hardware_kardex_prepare_fetch_payload(
                cell_location=cell_location
            )
            _logger.debug("Sending to kardex (fetch): {}", payload)
        else:
            payload = super()._hardware_vertical_lift_fetch_tray_payload(
                cell_location=cell_location
            )
        return payload
