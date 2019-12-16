# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

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

    @api.model
    def _selection_hardware(self):
        values = super()._selection_hardware()
        values += [("kardex", "Kardex")]
        return values

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
