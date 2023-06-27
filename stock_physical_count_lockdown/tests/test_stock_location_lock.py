# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockLocationLockdown(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestStockLocationLockdown, self).setUp(*args, **kwargs)

        # Create a new stock location with no quants and blocked stock entrance
        new_loc = {"name": "location_test", "usage": "internal"}
        self.new_stock_location = self.env["stock.location"].create(new_loc)
        self.new_stock_location.is_physical_count_lockdown = True

        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")

        self.update_location_lock_wizard = self.env["stock.location.lock"]

        # Call an existing product and force no Lot/Serial Number tracking
        self.product = self.env.ref("product.product_product_27")
        self.product.tracking = "none"

        # Catch the first quant's stock location
        self.stock_location = self.env["stock.quant"].search([])[0].location_id

    def test_transfer_stock_in_locked_location(self):
        """
        Test to move stock within a location that should not accept
        stock entrance.
        """
        move_vals = {
            "location_id": self.supplier_location.id,
            "location_dest_id": self.new_stock_location.id,
            "product_id": self.product.id,
            "product_uom_qty": self.product.qty_available + 1,
            "product_uom": 1,
            "name": "test",
            "move_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_qty": 0,
                        "product_uom_id": 1,
                        "qty_done": self.product.qty_available + 1,
                        "location_id": self.supplier_location.id,
                        "location_dest_id": self.new_stock_location.id,
                    },
                )
            ],
        }
        stock_move = self.env["stock.move"].create(move_vals)

        with self.assertRaises(ValidationError):
            stock_move._action_done()

    def test_transfer_stock_out_locked_location(self):
        """
        Test to move stock out from a location that should not accept
        stock removal.
        """
        move_vals = {
            "location_id": self.new_stock_location.id,
            "location_dest_id": self.customer_location.id,
            "product_id": self.product.id,
            "product_uom_qty": self.product.qty_available + 1,
            "product_uom": 1,
            "name": "test",
            "move_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_qty": 0,
                        "product_uom_id": 1,
                        "qty_done": self.product.qty_available + 1,
                        "location_id": self.supplier_location.id,
                        "location_dest_id": self.new_stock_location.id,
                    },
                )
            ],
        }
        stock_move = self.env["stock.move"].create(move_vals)

        with self.assertRaises(ValidationError):
            stock_move._action_done()

    def test_execute_button_wizard(self):
        self.new_stock_location.is_physical_count_lockdown = False
        self.update_location_lock_wizard.create(
            {
                "location_ids": self.new_stock_location,
            }
        ).execute()
        self.assertEqual(self.new_stock_location.is_physical_count_lockdown, True)
