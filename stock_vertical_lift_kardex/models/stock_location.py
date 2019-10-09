# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


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
        """
        if self.vertical_lift_shuttle_id.hardware == "kardex":
            payload = self._hardware_kardex_prepare_payload()
            # TODO implement the communication with kardex
        super()._hardware_vertical_lift_tray(cell_location=cell_location)
