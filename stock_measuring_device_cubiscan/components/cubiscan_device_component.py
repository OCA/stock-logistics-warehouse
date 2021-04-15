# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from cubiscan.cubiscan import CubiScan

from odoo import _, exceptions

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class CubiscanDevice(Component):
    _name = "device.component.cubiscan"
    _inherit = "measuring.device.base"
    _usage = "cubiscan"

    def test_device(self):
        """Check connection with the Cubiscan device"""
        res = self._get_interface().test()
        return res and "error" not in res

    def _get_interface(self):
        args, kwargs = self._get_interface_client_args()
        return CubiScan(*args, **kwargs)

    def _get_interface_client_args(self):
        """Prepare the arguments to instanciate the CubiScan client

        Can be overriden to change the parameters.

        Example, adding a ssl certificate::

            args, kwargs = super()._get_interface_client_args()
            ctx = SSL.create_default_context()
            ctx.load_cert_chain("/usr/lib/ssl/certs/my_cert.pem")
            kwargs['ssl'] = ctx
            return args, kwargs

        Returns a 2 items tuple with: (args, kwargs) where args
        is a list and kwargs a dict.
        """
        device = self.collection
        return ([device.device_address, device.port, device.timeout], {})

    def get_measure(self):
        """Return a measure from the Cubiscan device"""
        device = self.collection
        if device.state != "ready":
            raise exceptions.UserError(
                _(
                    "Device is not ready. Please use the 'Test'"
                    " button before using the device."
                )
            )
        measures = self._get_interface().measure()
        device._update_packaging_measures(measures)

    def preprocess_measures(self, measures):
        return {
            "max_weight": measures["weight"][0],
            "lngth": measures["length"][0] * 1000,
            "width": measures["width"][0] * 1000,
            "height": measures["height"][0] * 1000,
        }
