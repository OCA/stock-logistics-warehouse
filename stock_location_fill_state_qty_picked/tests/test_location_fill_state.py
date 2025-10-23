# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_location_fill_state.tests.common import LocationFillStateCommon


class TestLocationFillState(LocationFillStateCommon):
    def test_location_fill_state(self):
        self.assertEqual(
            "empty",
            self.stock_1.fill_state,
        )
        # Add a movement to fill in Stock 1
        move = self.env["stock.move"].create(
            {
                "name": "Product",
                "product_uom_qty": "2.0",
                "location_id": self.suppliers.id,
                "location_dest_id": self.stock_1.id,
                "product_id": self.product.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        self.assertEqual(
            "being_filled",
            self.stock_1.fill_state,
        )
        move.move_line_ids.qty_picked = 2.0
        move._action_done()
        self.assertEqual(
            "filled",
            self.stock_1.fill_state,
        )
        # Add a movement to empty Stock 1
        move = self.env["stock.move"].create(
            {
                "name": "Product",
                "product_uom_qty": "2.0",
                "location_id": self.stock_1.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "product_id": self.product.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        move.move_line_ids.qty_picked = 1.0
        self.assertEqual(
            "filled",
            self.stock_1.fill_state,
        )
        move.move_line_ids.qty_picked = 2.0
        self.assertEqual(
            "being_emptied",
            self.stock_1.fill_state,
        )
