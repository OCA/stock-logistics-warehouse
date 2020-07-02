# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPutawayMethod(TransactionCase):

    # Check if "fixed" is a valid putaway method
    def test_01_putaway_methods(self):
        field_method = self.env["stock.putaway.rule"]._fields.get("method")
        self.assertIn("fixed", field_method.get_values(self.env))
