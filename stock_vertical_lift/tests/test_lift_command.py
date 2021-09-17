# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tools import mute_logger

from .common import VerticalLiftCase


class TestLiftCommand(VerticalLiftCase):
    def test_lift_commands(self):
        self.shuttle.switch_inventory()
        command_id = self.shuttle.command_ids[0]
        message = "Unknown record"
        method_name = "odoo.addons.stock_vertical_lift.models.vertical_lift_command"
        with mute_logger(method_name):
            with self.assertRaisesRegex(exceptions.UserError, message):
                command_id.record_answer("0|test|1")
        command_id.record_answer("0|{}|1".format(command_id.name))
        self.shuttle.command_ids.create(
            {
                "shuttle_id": self.shuttle.id,
                "command": "0|test|1",
            }
        )
