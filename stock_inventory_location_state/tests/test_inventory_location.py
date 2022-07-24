# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockInventoryLocationState(TransactionCase):
    def setUp(self):
        super(TestStockInventoryLocationState, self).setUp()
        self.location = self.env.ref("stock.warehouse0").lot_stock_id

    def test_inventory_location(self):
        inventory = self.env["stock.inventory"].create(
            {"location_ids": [(6, 0, self.location.ids)]}
        )
        inventory.action_start()
        sub_locations = self.env["stock.location"].search(
            [("id", "child_of", self.location.id), ("child_ids", "=", False)]
        )
        self.assertEqual(
            inventory.sub_location_ids.mapped("location_id"), sub_locations
        )
        inventory.sub_location_ids[0].state = "done"
        with self.assertRaises(UserError):
            inventory.action_validate()
        inventory.sub_location_ids.write({"state": "done"})
        inventory.action_validate()
