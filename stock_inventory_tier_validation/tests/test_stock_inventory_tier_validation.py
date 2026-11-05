# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, new_test_user


class TestStockInventoryTierValidation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.company.stock_inventory_auto_complete = False
        cls.reviewer = new_test_user(
            cls.env, login="inventory_reviewer", groups="stock.group_stock_manager"
        )
        cls.tier_definition = cls.env["tier.definition"].create(
            {
                "model_id": cls.env.ref("stock_inventory.model_stock_inventory").id,
                "review_type": "individual",
                "reviewer_id": cls.reviewer.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Test Location",
                "usage": "internal",
                "location_id": cls.env.ref("stock.stock_location_stock").id,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.location, 10.0
        )
        cls.quant = cls.env["stock.quant"].search(
            [("product_id", "=", cls.product.id), ("location_id", "=", cls.location.id)]
        )
        cls.inventory = cls.env["stock.inventory"].create(
            {
                "name": "Test Adjustment",
                "location_ids": [Command.set(cls.location.ids)],
            }
        )

    def _count(self, qty):
        self.inventory.action_state_to_in_progress()
        self.quant.inventory_quantity = qty

    def test_apply_after_validation(self):
        self._count(7.0)
        with self.assertRaises(ValidationError):
            self.inventory.action_state_to_done()
        self.inventory.request_validation()
        self.assertEqual(self.inventory.validation_status, "pending")
        with self.assertRaises(ValidationError):
            self.inventory.action_state_to_done()
        self.assertEqual(self.quant.quantity, 10.0)
        self.inventory.with_user(self.reviewer).validate_tier()
        self.assertEqual(self.inventory.validation_status, "validated")
        self.inventory.action_state_to_done()
        self.assertEqual(self.inventory.state, "done")
        self.assertEqual(self.quant.quantity, 7.0)
        self.assertEqual(self.inventory.stock_move_ids.qty_done, 3.0)
        self.assertFalse(self.quant.current_inventory_id)

    def test_quant_apply_blocked(self):
        self.assertTrue(self.quant.inventory_tier_validation_required)
        self.quant.inventory_quantity = 5.0
        with self.assertRaises(UserError):
            self.quant.action_apply_inventory()
        self.quant.action_set_inventory_quantity_to_zero()
        # Inside an adjustment that is not done yet
        self._count(5.0)
        with self.assertRaises(UserError):
            self.quant.action_apply_inventory()
        self.assertEqual(self.quant.quantity, 10.0)

    def test_no_tier_definition(self):
        self.tier_definition.active = False
        self.quant.invalidate_recordset(["inventory_tier_validation_required"])
        self.assertFalse(self.quant.inventory_tier_validation_required)
        self.quant.inventory_quantity = 8.0
        self.quant.action_apply_inventory()
        self.assertEqual(self.quant.quantity, 8.0)
        # Set to Done does not apply counts, as in stock_inventory
        self._count(6.0)
        self.inventory.action_state_to_done()
        self.assertEqual(self.inventory.state, "done")
        self.assertEqual(self.quant.quantity, 8.0)

    def test_counted_quantity_frozen_under_validation(self):
        self._count(7.0)
        self.inventory.request_validation()
        with self.assertRaises(UserError):
            self.quant.inventory_quantity = 6.0
        self.inventory.with_user(self.reviewer).reject_tier()
        self.quant.inventory_quantity = 6.0
        self.inventory.restart_validation()
        self.assertFalse(self.inventory.review_ids)
        self.quant.inventory_quantity = 5.0
        self.assertEqual(self.quant.inventory_quantity, 5.0)

    def test_outdated_count(self):
        self._count(7.0)
        # Store the difference as of the count, as the end of a request would
        self.env.flush_all()
        self.inventory.request_validation()
        self.inventory.with_user(self.reviewer).validate_tier()
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location, 1.0
        )
        with self.assertRaises(UserError):
            self.inventory.action_state_to_done()
        self.assertEqual(self.inventory.state, "in_progress")

    def _validate_and_done(self, inventory):
        inventory.request_validation()
        inventory.with_user(self.reviewer).validate_tier()
        inventory.action_state_to_done()

    def test_next_adjustment_same_location(self):
        self._count(7.0)
        self._validate_and_done(self.inventory)
        self.assertFalse(self.quant.inventory_quantity_set)
        self.assertFalse(self.quant.is_outdated)
        inventory = self.inventory.copy(
            {"location_ids": [Command.set(self.location.ids)]}
        )
        inventory.action_state_to_in_progress()
        self._validate_and_done(inventory)
        self.assertEqual(inventory.state, "done")
        self.assertEqual(self.quant.quantity, 7.0)

    def test_line_added_during_count(self):
        self.inventory.action_state_to_in_progress()
        product = self.env["product.product"].create(
            {"name": "Found Product", "type": "product"}
        )
        quant = (
            self.env["stock.quant"]
            .with_context(
                active_model="stock.inventory",
                active_id=self.inventory.id,
                inventory_mode=True,
                default_to_do=True,
            )
            .create(
                {
                    "product_id": product.id,
                    "location_id": self.location.id,
                    "inventory_quantity": 4.0,
                }
            )
        )
        self.assertEqual(quant.current_inventory_id, self.inventory)
        self._validate_and_done(self.inventory)
        self.assertEqual(quant.quantity, 4.0)

    def test_done_with_validation_exception(self):
        self.env["tier.validation.exception"].create(
            {
                "model_id": self.env.ref("stock_inventory.model_stock_inventory").id,
                "field_ids": [
                    Command.set(
                        self.env.ref(
                            "stock_inventory.field_stock_inventory__responsible_id"
                        ).ids
                    )
                ],
                "allowed_to_write_under_validation": True,
            }
        )
        self._count(7.0)
        self._validate_and_done(self.inventory)
        self.assertEqual(self.inventory.state, "done")
        self.assertEqual(self.quant.quantity, 7.0)

    def test_tier_definition_other_company(self):
        self.tier_definition.company_id = self.env["res.company"].create(
            {"name": "Other Company"}
        )
        self.assertFalse(self.quant.inventory_tier_validation_required)
        self._count(7.0)
        self.inventory.action_state_to_done()
        self.assertEqual(self.inventory.state, "done")
        self.assertEqual(self.quant.quantity, 10.0)
