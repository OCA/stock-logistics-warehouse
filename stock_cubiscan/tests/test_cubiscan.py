# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from cubiscan.cubiscan import CubiScan
from mock import patch

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestCubiscan(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.device_obj = cls.env["cubiscan.device"]

    def test_constraints(self):
        vals = {"name": "Test Device"}

        # Wrong port
        vals.update({"device_address": "10.10.0.42", "port": -42})
        with self.assertRaises(ValidationError):
            self.device_obj.create(vals)

    def test_device_test(self):
        vals = {"name": "Test Device", "device_address": "10.10.0.42", "port": 5982}
        device = self.device_obj.create(vals)
        self.assertEquals(device.state, "not_ready")

        with patch.object(CubiScan, "_make_request") as mocked:
            mocked.return_value = {"identifier": 42}
            device.test_device()

        self.assertEquals(device.state, "ready")
