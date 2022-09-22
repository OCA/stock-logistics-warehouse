# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockInventoryLocationState(TransactionCase):
    def setUp(self):
        super(TestStockInventoryLocationState, self).setUp()
        self.location = self.env.ref("stock.warehouse0").lot_stock_id
        self.child_loc = self.env["stock.location"].search(
            [("id", "child_of", self.location.id), ("child_ids", "=", False)]
        )[0]
        self.product = self.env["product.product"].create(
            {"name": "Test", "type": "product"}
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.child_loc, 1
        )

    def test_inventory_location(self):
        inventory = self.env["stock.inventory"].create(
            {"location_ids": [(6, 0, self.location.ids)]}
        )
        inventory.action_start()
        sub_locations = self.env["stock.location"].search(
            [("id", "child_of", self.location.id), ("child_ids", "=", False)]
        )
        self.assertEqual(inventory.sub_location_ids.location_id, sub_locations)
        inventory.sub_location_ids[0].action_start()
        inventory.sub_location_ids[0].action_done()
        self.assertEqual(inventory.location_count, len(sub_locations))
        self.assertEqual(inventory.location_done_count + 1, len(sub_locations))
        with self.assertRaises(UserError):
            inventory.action_validate()
        inventory.sub_location_ids.write({"state": "done"})
        inventory.action_validate()

    def test_action_start(self):
        inventory = self.env["stock.inventory"].create(
            {"location_ids": [(6, 0, self.location.ids)]}
        )
        inventory.action_start()
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.child_loc, 1
        )
        line = inventory.line_ids.filtered(
            lambda l: l.product_id == self.product and l.location_id == self.child_loc
        )
        self.assertEqual(line.theoretical_qty, 1)
        sub_location = inventory.sub_location_ids.filtered(
            lambda l: l.location_id == self.child_loc
        )
        sub_location.action_start()
        self.assertEqual(sub_location.state, "started")
        self.assertEqual(line.theoretical_qty, 2)
