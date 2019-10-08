# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import models

_logger = logging.getLogger(__name__)


class StockLocation(models.Model):
    _inherit = 'stock.location'

    def _hardware_kardex_prepare_payload(self, cell_location=None):
        return ""

    def _hardware_vertical_lift_tray(self, cell_location=None):
        """Send instructions to the vertical lift hardware

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
            payload = self._hardware_kardex_prepare_payload()
            _logger.debug("Sending to kardex: {}", payload)
            # TODO implement the communication with kardex
        super()._hardware_vertical_lift_tray(cell_location=cell_location)
