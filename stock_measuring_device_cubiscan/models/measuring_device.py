# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import _, api, exceptions, fields, models


class MeasuringDevice(models.Model):
    _inherit = "measuring.device"

    device_type = fields.Selection(selection_add=[("cubiscan", "Cubiscan")])
    device_address = fields.Char("Device IP Address", copy=False)
    port = fields.Integer("Port")
    timeout = fields.Integer("Timeout", help="Timeout in seconds", default=30)

    @api.constrains("device_address", "port")
    def _check_connection_infos(self):
        self.ensure_one()
        if not 1 <= self.port <= 65535:
            raise exceptions.ValidationError(_("Port must be in range 1-65535"))
