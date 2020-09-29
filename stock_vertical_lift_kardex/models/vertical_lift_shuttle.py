# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


JMIF_STATUS = {
    0: "success",
    101: "common error",
    102: "sequence number invalid",
    103: "machine busy",
    104: "timeout",
    105: "max retry reached",
    106: "carrier in use or undefined",
    107: "cancelled",
    108: "invalid user input data",
    201: "request accepted and queued",
    202: "request processing started / request active",
    203: "carrier arrived, maybe overwritten by code 0",
    301: "AO occupied with other try on move back (store / put)",
    302: "AO occupied with other try on fetch (pick)",
}


class VerticalLiftShuttle(models.Model):
    _inherit = "vertical.lift.shuttle"

    def _selection_hardware(self):
        values = super()._selection_hardware()
        values += [("kardex", "Kardex")]
        return values

    _kardex_message_template = (
        "{code}|{hostId}|{addr}|{carrier}|{carrierNext}|"
        "{x}|{y}|{boxType}|{Q}|{order}|{part}|{desc}|\r\n"
    )

    def _hardware_kardex_format_template(self, values):
        payload = self._kardex_message_template.format(**values)
        return payload.encode("iso-8859-1", "replace")

    def _kardex_shuttle_code(self):
        mapping = {"pick": "1", "put": "2", "inventory": "5"}
        ping = "61"
        return mapping.get(self.mode, ping)

    def _hardware_kardex_prepare_release_payload(self):
        subst = {
            "code": self._kardex_shuttle_code(),
            "hostId": self.env["ir.sequence"].next_by_code("vertical.lift.command"),
            # hard code the gate for now.
            "addr": self.name + "-1",
            "carrier": "0",
            "carrierNext": "0",
            "x": "0",
            "y": "0",
            "boxType": "",
            "Q": "",
            "order": "",
            "part": "",
            "desc": "",
        }
        return self._hardware_kardex_format_template(subst)

    def _hardware_vertical_lift_release_tray_payload(self):
        """Prepare "release" message to be sent to the vertical lift hardware

        Private method, this is where the implementation actually happens.
        Addons can add their instructions based on the hardware used for
        this location.

        The hardware used for a location can be found in:

        ``self.vertical_lift_shuttle_id.hardware``

        Each addon can implement its own mechanism depending of this value
        and must call ``super``.

        The method must send the command to the vertical lift to release (close)
        the tray.

        Returns a message in bytes, that will be sent through
        ``VerticalLiftShuttle._hardware_send_message()``.
        """
        if self.hardware == "kardex":
            payload = self._hardware_kardex_prepare_release_payload()
            _logger.debug("Sending to kardex (release): {}", payload)
        else:
            payload = super()._hardware_vertical_lift_release_tray_payload()
        return payload

    def _check_server_response(self, command):
        response = command.answer
        code, sep, remaining = response.partition("|")
        code = int(code)
        if code == 0:
            return True
        elif 1 <= code <= 99:
            command.error = "interface error %d" % code
            return False
        elif code in JMIF_STATUS and code < 200:
            command.error = "%d: %s" % (code, JMIF_STATUS[code])
            return False
        elif code in JMIF_STATUS and code < 300:
            command.error = "%d: %s" % (code, JMIF_STATUS[code])
            return True
        elif code in JMIF_STATUS:
            command.error = "%d: %s" % (code, JMIF_STATUS[code])
        elif 501 <= code <= 999:
            command.error = "%d: %s" % (code, "MM260 Error")
        elif 1000 <= code <= 32767:
            command.error = "%d: %s" % (code, "C2000TCP/C3000CGI machine error")
        elif 0xFF0 <= code == 0xFFF:
            command.error = "{:x}: {}".format(
                code, "C3000CGI machine error (global short)"
            )
        elif 0xFFF < code:
            command.error = "{:x}: {}".format(code, "C3000CGI machine error (long)")
        return False
