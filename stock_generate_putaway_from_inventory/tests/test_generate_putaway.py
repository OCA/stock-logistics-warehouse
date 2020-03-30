# Copyright Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestGeneratePutaway(TransactionCase):
    def setUp(self):
        super().setUp()
        ref = self.env.ref
        # demo data
        self.inventory_location = ref("stock.stock_location_stock")
        self.inventory = self.env["stock.inventory"].create(
            {
                "name": "example inventory",
                "location_id": self.inventory_location.id,
            }
        )
        self.inventory_line_1_product = ref("product.product_product_24")
        self.inventory_line_1_location = ref("stock.stock_location_14")
        self.inventory_line_1 = self.env["stock.inventory.line"].create(
            {
                "product_id": self.inventory_line_1_product.id,
                "location_id": self.inventory_line_1_location.id,
            }
        )
        self.irrelevant_location = ref("stock.stock_location_customers")

    def test_error_not_validated(self):
        putaway = self.env["product.putaway"].create(
            {"name": "Putaway example"}
        )
        self.inventory.putaway_strategy_id = putaway
        self.inventory.action_cancel_draft()
        with self.assertRaises(ValidationError):
            self.inventory.action_generate_putaway_strategy()

    def test_error_location_has_no_putaway_strategy(self):
        self.inventory_location.putaway_strategy_id = self.env[
            "product.putaway"
        ]
        self.inventory.action_start()
        self.inventory.action_validate()
        with self.assertRaises(ValidationError):
            self.inventory.action_generate_putaway_strategy()

    def test_putaway_line_location_update(self):
        putaway = self.env["product.putaway"].create(
            {"name": "Putaway example"}
        )
        putaway_line_1 = self.env["stock.fixed.putaway.strat"].create(
            {
                "putaway_id": putaway.id,
                "fixed_location_id": self.irrelevant_location.id,
                "product_id": self.inventory_line_1_product.id,
            }
        )
        self.inventory_location.putaway_strategy_id = putaway
        self.inventory.action_start()
        self.inventory.action_validate()
        self.inventory.action_generate_putaway_strategy()
        self.assertEqual(
            putaway_line_1.fixed_location_id, self.inventory_line_1_location
        )

    def test_putaway_line_location_create(self):
        putaway = self.env["product.putaway"].create(
            {"name": "Putaway example"}
        )
        self.inventory_location.putaway_strategy_id = putaway
        self.inventory.action_start()
        self.inventory.action_validate()
        self.inventory.action_generate_putaway_strategy()
        putaway_line = putaway.product_location_ids.filtered(
            lambda r: r.product_id == self.inventory_line_1_product
        )
        self.assertEqual(
            putaway_line.fixed_location_id, self.inventory_line_1_location
        )
