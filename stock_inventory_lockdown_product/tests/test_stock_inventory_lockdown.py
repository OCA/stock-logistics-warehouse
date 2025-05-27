from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.stock.tests.common import TestStockCommon


@tagged("-at_install", "post_install")
class StockInventoryLocationTest(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.use_soft_inventory_lock = True
        cls.internal_location = cls.env["stock.location"].create(
            {
                "name": "Test location",
                "usage": "internal",
            }
        )

        # Add stock for two products
        cls.env["stock.quant"].create(
            {
                "location_id": cls.internal_location.id,
                "product_id": cls.productA.id,
                "quantity": 100.0,
            }
        )
        cls.env["stock.quant"].create(
            {
                "location_id": cls.internal_location.id,
                "product_id": cls.productB.id,
                "quantity": 50.0,
            }
        )

    def create_stock_move(self, product, origin_id=False, dest_id=False):
        return self.env["stock.move"].create(
            {
                "name": "Test move lock down",
                "product_id": product.id,
                "product_uom_qty": 10.0,
                "product_uom": product.uom_id.id,
                "location_id": origin_id or self.supplier_location.id,
                "location_dest_id": dest_id or self.customer_location,
            }
        )

    def test_move_product_in_inventory_should_fail(self):
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Lock down location",
                "location_ids": [(4, self.internal_location.id)],
                "product_ids": [(4, self.productA.id)],
            }
        )
        inventory.action_state_to_in_progress()
        move = self.create_stock_move(
            product=self.productA,
            origin_id=self.internal_location.id,
            dest_id=self.customer_location,
        )
        move._action_confirm()
        move._action_assign()
        move.move_line_ids.qty_done = 5
        with self.assertRaises(ValidationError):
            move._action_done()

    def test_move_product_not_in_inventory_should_pass(self):
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Lock down location",
                "location_ids": [(4, self.internal_location.id)],
                "product_ids": [(4, self.productA.id)],
            }
        )
        inventory.action_state_to_in_progress()
        move = self.create_stock_move(
            product=self.productB,
            origin_id=self.internal_location.id,
            dest_id=self.customer_location,
        )
        move._action_confirm()
        move._action_assign()
        move.move_line_ids.qty_done = 5
        move._action_done()  # Should not raise

    def test_soft_lock_disabled_should_block_any_product(self):
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Lock down location",
                "location_ids": [(4, self.internal_location.id)],
                "product_ids": [(4, self.productA.id)],
            }
        )
        inventory.action_state_to_in_progress()
        self.env.company.use_soft_inventory_lock = False
        move = self.create_stock_move(
            product=self.productB,
            origin_id=self.internal_location.id,
            dest_id=self.customer_location,
        )
        move._action_confirm()
        move._action_assign()
        move.move_line_ids.qty_done = 10.0
        with self.assertRaises(ValidationError):
            move._action_done()
