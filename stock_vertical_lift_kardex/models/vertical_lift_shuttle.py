# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class VerticalLiftShuttle(models.Model):
    _inherit = 'vertical.lift.shuttle'

    @api.model
    def _selection_hardware(self):
        values = super()._selection_hardware()
        values += [('kardex', 'Kardex')]
        return values

    def _hardware_recv_response(self, conn):
        # the implementation uses messages delimited with \r\n
        response = b''
        chunk = True
        while chunk:
            chunk = conn.recv(1)
            response += chunk
            if response.endswith(b'\r\n'):
                break
        return response

    def _check_server_response(self, payload, response):
        payload = payload.decode('iso-8859-1')
        response = response.decode('iso-8859-1')
        code, sep, remaining = response.partition('|')
        return code == "0"
