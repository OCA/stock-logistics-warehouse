# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class VerticalLiftShuttle(models.Model):
    _name = "vertical.lift.shuttle"
    _inherit = ["vertical.lift.shuttle", "server.env.mixin"]

    @property
    def _server_env_fields(self):
        base_fields = super()._server_env_fields
        sftp_fields = {
            "hardware": {"compute_default": "_compute_default_hardware"},
            "server": {},
            "port": {},
            "use_tls": {},
        }
        sftp_fields.update(base_fields)
        return sftp_fields

    def _compute_default_hardware(self):
        self.update({"hardware": "simulation"})
