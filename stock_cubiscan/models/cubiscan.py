# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ssl as SSL

from cubiscan.cubiscan import CubiScan

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class CubiscanDevice(models.Model):
    _name = "cubiscan.device"
    _description = "Cubiscan Device"
    _order = "warehouse_id, name"

    name = fields.Char("Name", required=True)
    device_address = fields.Char("Device IP Address", required=True)
    port = fields.Integer("Port", required=True)
    timeout = fields.Integer(
        "Timeout", help="Timeout in seconds", required=True, default=30
    )
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")
    state = fields.Selection(
        [("not_ready", "Not Ready"), ("ready", "Ready")],
        default="not_ready",
        readonly=True,
        copy=False,
    )

    @api.constrains("device_address", "port")
    def _check_connection_infos(self):
        self.ensure_one()
        if not 1 <= self.port <= 65535:
            raise ValidationError(_("Port must be in range 1-65535"))

    def open_wizard(self):
        self.ensure_one()
        return {
            "name": _("CubiScan Wizard"),
            "res_model": "cubiscan.wizard",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "form",
            "context": {"default_device_id": self.id},
            "target": "fullscreen",
            "flags": {
                "withControlPanel": False,
                "form_view_initial_mode": "edit",
                "no_breadcrumbs": True,
            },
        }

    def _get_interface(self):
        """Return the CubiScan client

        Can be overrided to customize the way it is instanciated
        """
        self.ensure_one()
        ctx = SSL.create_default_context()
        ctx.load_cert_chain("/usr/lib/ssl/certs/camptocamp.pem")
        ctx.check_hostname = False
        ctx.verify_mode = SSL.CERT_NONE
        return CubiScan(self.device_address, self.port, self.timeout, ssl=ctx)

    def test_device(self):
        """Check connection with the Cubiscan device"""
        for device in self:
            res = device._get_interface().test()
            if res and "error" not in res and device.state == "not_ready":
                device.state = "ready"
            elif res and "error" in res and device.state == "ready":
                device.state = "not_ready"

    def get_measure(self):
        """Return a measure from the Cubiscan device"""
        self.ensure_one()
        if self.state != "ready":
            raise UserError(
                _(
                    "Device is not ready. Please use the 'Test'"
                    " button before using the device."
                )
            )
        return self._get_interface().measure()
