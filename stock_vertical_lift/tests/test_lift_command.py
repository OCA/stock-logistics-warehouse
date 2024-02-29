# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo import exceptions, fields
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

    @mute_logger("odoo.addons.stock_vertical_lift.models.vertical_lift_command")
    def test_lift_commands_autovacuum(self):
        command_obj = self.env["vertical.lift.command"]
        param_obj = self.env["ir.config_parameter"].sudo()
        param_key = "stock_vertical_lift.delete_command_after_days"

        # Create 1 new command for the test
        vals = {"name": "Test", "command": "Test", "shuttle_id": self.shuttle.id}
        command = command_obj.create(vals)
        create_date = command.create_date.date()

        # Test 1: param ``stock_vertical_lift.delete_command_after_days`` not set
        # => command not deleted
        param_obj.search([("key", "=", param_key)]).unlink()
        command_obj._autovacuum_commands()
        self.assertTrue(command.exists())

        # Test 2: param ``stock_vertical_lift.delete_command_after_days`` set, but
        # the given value is not an integer
        # => command not deleted
        param_obj.set_param(param_key, "asd")
        command_obj._autovacuum_commands()
        self.assertTrue(command.exists())

        # Test 3: param ``stock_vertical_lift.delete_command_after_days`` set, but
        # the command is created later than the time limit (limit is 10 days, method is
        # executed 5 days after the command creation)
        # => command not deleted
        param_obj.set_param(param_key, 10)
        with freeze_time(fields.Date.add(create_date, days=5)):
            command_obj._autovacuum_commands()
        self.assertTrue(command.exists())

        # Test 4: param ``stock_vertical_lift.delete_command_after_days`` set, and
        # the command is created earlier than the time limit (limit is 10 days, method
        # is executed 15 days after the command creation)
        # => command not deleted
        param_obj.set_param(param_key, 10)
        with freeze_time(fields.Date.add(create_date, days=15)):
            command_obj._autovacuum_commands()
        self.assertFalse(command.exists())
