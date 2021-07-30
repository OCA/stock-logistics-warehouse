# Copyright Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestGeneratePutaway(TransactionCase):
    def setUp(self):
        super().setUp()
        ref = self.env.ref
        # demo data
        self.inventory_location = ref("stock.stock_location_stock")
        self.inventory_location._compute_children_ids()
        self.inventory = self.env["stock.inventory"].create(
            {
                "name": "example inventory",
                "location_ids": [(6, 0, [self.inventory_location.id])],
            }
        )
        self.inventory_line_1_product = ref("product.product_product_24")
        self.inventory_line_1_location = ref("stock.stock_location_components")
        self.inventory_line_1 = self.env["stock.inventory.line"].create(
            {
                "product_id": self.inventory_line_1_product.id,
                "location_id": self.inventory_line_1_location.id,
                "inventory_id": self.inventory.id,
                "product_qty": 1,
            }
        )
        self.irrelevant_location = ref("stock.stock_location_customers")

    def test_error_not_validated(self):
        self.inventory.action_cancel_draft()
        with self.assertRaises(ValidationError):
            self.inventory.action_generate_putaway_rules()

    def test_putaway_line_location_update(self):
        putaway = self.env["stock.putaway.rule"].create(
            {
                "location_out_id": self.irrelevant_location.id,
                "location_in_id": self.inventory_location.id,
                "product_id": self.inventory_line_1_product.id,
            }
        )
        self.inventory.action_start()
        self.inventory.action_validate()
        self.inventory.action_generate_putaway_rules()
        self.assertEqual(putaway.location_out_id, self.inventory_line_1_location)

    def test_putaway_line_location_create(self):
        self.inventory.action_start()
        self.inventory.action_validate()
        self.inventory.action_generate_putaway_rules()
        putaway = self.env["stock.putaway.rule"].search(
            [
                ("product_id", "=", self.inventory_line_1_product.id),
                ("location_in_id", "=", self.inventory_location.id),
            ]
        )
        self.assertEqual(putaway.location_out_id, self.inventory_line_1_location)
