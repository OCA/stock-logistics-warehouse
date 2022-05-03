# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import unittest

import mock

from odoo.tests.common import HttpSavepointCase
from odoo.tools import mute_logger

CTRL_PATH = "odoo.addons.stock_vertical_lift.controllers.main.VerticalLiftController"


@unittest.skipIf(os.getenv("SKIP_HTTP_CASE"), "HttpCase skipped")
class TestController(HttpSavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.shuttle = cls.env.ref(
            "stock_vertical_lift.stock_vertical_lift_demo_shuttle_1"
        )

    @mute_logger("werkzeug")
    def test_fail(self):
        data = {"answer": "got it!", "secret": "wrong"}
        with self.assertLogs(level="ERROR") as log_catcher:
            response = self.url_open("/vertical-lift", data=data)
            self.assertEqual(response.status_code, 401)
            logger = "odoo.addons.stock_vertical_lift.controllers.main:secret"
            self.assertEqual(log_catcher.output[0], f"ERROR:{logger} mismatch: 'wrong'")

    def test_record_answer(self):
        self.shuttle.command_ids.create(
            {
                "shuttle_id": self.shuttle.id,
                "command": "0|test|1",
            }
        )
        with mock.patch(CTRL_PATH + "._get_env_secret") as mocked:
            mocked.return_value = "SECRET"
            data = {"answer": "0|test|2", "secret": "SECRET"}
            response = self.url_open("/vertical-lift", data=data)
            self.assertEqual(response.status_code, 200)
            self.shuttle.command_ids.invalidate_cache()
            self.assertEqual(self.shuttle.command_ids[0].answer, data["answer"])
