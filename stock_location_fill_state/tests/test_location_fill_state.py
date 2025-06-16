# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.osv.expression import AND

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.stock_location_pending_move.models.stock_location import (
    PENDING_MOVE_DOMAIN,
)


class TestLocationFillState(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.suppliers = cls.env.ref("stock.stock_location_suppliers")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
            }
        )
        cls.stock_1 = cls.env["stock.location"].create(
            {
                "name": "Stock 1",
                "location_id": cls.stock.id,
            }
        )
        cls.stock_2 = cls.env["stock.location"].create(
            {
                "name": "Stock 2",
                "location_id": cls.stock.id,
                "exclude_from_fill_state_computation": True,
            }
        )

    def test_location_fill_state(self):
        # Check the multi call
        (self.stock_1 | self.stock).mapped("fill_state")
        self.assertEqual("filled", self.stock.fill_state)
        self.assertEqual("empty", self.stock_1.fill_state)
        stock = self.stock.search([("fill_state", "=", "empty")])
        self.assertIn(
            self.stock_1.id,
            stock.ids,
        )
        self.assertNotIn(
            self.stock.id,
            stock.ids,
        )
        # Search with the is_void == True domain
        stock = self.stock.search([("fill_state", "=", "filled")])
        self.assertNotIn(
            self.stock_1.id,
            stock.ids,
        )
        self.assertIn(
            self.stock.id,
            stock.ids,
        )

        # Add a movement to fill in Stock 1
        move = self.env["stock.move"].create(
            {
                "name": "Product",
                "product_uom_qty": "1.0",
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
        move.quantity_done = 1.0
        move._action_done()
        self.assertEqual(
            "filled",
            self.stock_1.fill_state,
        )
        # Add a movement to empty Stock 1
        move = self.env["stock.move"].create(
            {
                "name": "Product",
                "product_uom_qty": "1.0",
                "location_id": self.stock_1.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "product_id": self.product.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        move.quantity_done = 1.0
        self.assertEqual(
            "being_emptied",
            self.stock_1.fill_state,
        )

        # Check that the customers location is not computed
        self.assertFalse(self.customers.fill_state)
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": self.product.id,
                "location_id": self.customers.id,
                "inventory_quantity": 10.0,
            }
        )._apply_inventory()
        domain = AND(
            [PENDING_MOVE_DOMAIN, [("location_dest_id", "=", self.customers.id)]]
        )
        moves = self.env["stock.move"].search(domain)
        for move in moves:
            move.quantity_done = move.product_uom_qty
        moves._action_done()

        self.assertFalse(self.customers.fill_state)

    def test_location_fill_state_being_emptied_being_filled(self):
        # Check the multi call
        (self.stock_1 | self.stock).mapped("fill_state")
        self.assertEqual("filled", self.stock.fill_state)
        self.assertEqual("empty", self.stock_1.fill_state)
        stock = self.stock.search([("fill_state", "=", "empty")])
        self.assertIn(
            self.stock_1.id,
            stock.ids,
        )
        self.assertNotIn(
            self.stock.id,
            stock.ids,
        )
        # Search with the is_void == True domain
        stock = self.stock.search([("fill_state", "=", "filled")])
        self.assertNotIn(
            self.stock_1.id,
            stock.ids,
        )
        self.assertIn(
            self.stock.id,
            stock.ids,
        )

        # Add a movement to fill in Stock 1
        move = self.env["stock.move"].create(
            {
                "name": "Product",
                "product_uom_qty": "1.0",
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
        move.quantity_done = 1.0
        move._action_done()
        self.assertEqual(
            "filled",
            self.stock_1.fill_state,
        )
        # Add a movement to empty Stock 1
        move = self.env["stock.move"].create(
            {
                "name": "Product",
                "product_uom_qty": "1.0",
                "location_id": self.stock_1.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "product_id": self.product.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        move.quantity_done = 1.0
        self.assertEqual(
            "being_emptied",
            self.stock_1.fill_state,
        )

        # Add a move that is filling the location
        move = self.env["stock.move"].create(
            {
                "name": "Product",
                "product_uom_qty": "1.0",
                "location_id": self.suppliers.id,
                "location_dest_id": self.stock.id,
                "product_id": self.product.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        self.assertEqual(
            "being_emptied",
            self.stock_1.fill_state,
        )

        # Change the final destination
        move.move_line_ids.location_dest_id = self.stock_1
        self.assertEqual(
            "being_filled",
            self.stock_1.fill_state,
        )

    def test_exclude(self):
        # Check the locations that are set to not compute
        # the fill state get the False value.
        self.assertFalse(self.stock_2.fill_state)
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": self.product.id,
                "location_id": self.stock_2.id,
                "inventory_quantity": 10.0,
            }
        )._apply_inventory()
        self.assertFalse(self.stock_2.fill_state)
