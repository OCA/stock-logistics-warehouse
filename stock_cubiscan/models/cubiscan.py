# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ipaddress import ip_address

from cubiscan.cubiscan import CubiScan
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class CubiscanDevice(models.Model):
    _name = 'cubiscan.device'
    _description = 'Cubiscan Device'
    _order = 'warehouse_id, name'

    name = fields.Char('Name', required=True)
    device_address = fields.Char('Device IP Address', required=True)
    port = fields.Integer('Port', required=True)
    timeout = fields.Integer(
        'Timeout', help="Timeout in seconds", required=True, default=30
    )
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    state = fields.Selection(
        [('not_ready', 'Not Ready'), ('ready', 'Ready')],
        default='not_ready',
        readonly=True,
    )

    @api.multi
    @api.constrains('device_address', 'port')
    def _check_connection_infos(self):
        self.ensure_one()
        if not 1 <= self.port <= 65535:
            raise ValidationError('Port must be in range 1-65535')

        try:
            ip_address(self.device_address)
        except ValueError:
            raise ValidationError('Device IP Address is not valid')

    @api.multi
    def copy(self, default=None):
        if not default:
            default = dict()
        default['state'] = 'not_ready'
        return super().copy(default)

    @api.multi
    def open_wizard(self):
        self.ensure_one()
        return {
            'name': _('CubiScan Wizard'),
            'res_model': 'cubiscan.wizard',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'default_device_id': self.id},
            'target': 'fullscreen',
            'flags': {
                'headless': True,
                'form_view_initial_mode': 'edit',
                'no_breadcrumbs': True,
            },
        }

    @api.multi
    def _get_interface(self):
        self.ensure_one()
        return CubiScan(self.device_address, self.port, self.timeout)

    @api.multi
    def test_device(self):
        for device in self:
            res = device._get_interface().test()
            if res and 'error' not in res and device.state == 'not_ready':
                device.state = 'ready'
            elif res and 'error' in res and device.state == 'ready':
                device.state = 'not_ready'

    @api.multi
    def get_measure(self):
        self.ensure_one()
        if self.state != 'ready':
            raise UserError(
                "Device is not ready. Please use the 'Test' button before using the device."
            )
        return self._get_interface().measure()
