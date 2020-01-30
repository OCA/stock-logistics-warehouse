# Copyright 2017 Creu Blanca
# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from .base_test import TestBaseKanban


class TestKanban(TestBaseKanban):
    def setUp(self):
        super().setUp()
        self.main_company = self.env.ref("base.main_company")
        self.route = self.env["stock.location.route"].create(
            {
                "name": "Transfer",
                "product_categ_selectable": False,
                "product_selectable": True,
                "company_id": self.main_company.id,
                "sequence": 10,
            }
        )
        self.product = self.env["product.product"].create(
            {"name": "Product", "route_ids": [(4, self.route.id)], "company_id": False}
        )
        self.product_2 = self.env["product.product"].create(
            {
                "name": "Product 2",
                "route_ids": [(4, self.route.id)],
                "company_id": False,
            }
        )
        self.kanban_1 = self.env["stock.request.kanban"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_uom_qty": 1,
            }
        )
        self.kanban_2 = self.env["stock.request.kanban"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_uom_qty": 1,
            }
        )
        self.kanban_3 = self.env["stock.request.kanban"].create(
            {
                "product_id": self.product_2.id,
                "product_uom_id": self.product.uom_id.id,
                "product_uom_qty": 1,
            }
        )

    def test_inventory_warehouse(self):
        inventory = self.env["stock.inventory.kanban"].create(
            {"warehouse_ids": [(4, self.kanban_1.warehouse_id.id)]}
        )
        inventory.start_inventory()
        self.assertIn(self.kanban_1, inventory.kanban_ids)
        self.assertIn(self.kanban_1, inventory.missing_kanban_ids)

    def test_inventory_location(self):
        inventory = self.env["stock.inventory.kanban"].create(
            {"location_ids": [(4, self.kanban_1.location_id.id)]}
        )
        inventory.start_inventory()
        self.assertIn(self.kanban_1, inventory.kanban_ids)
        self.assertIn(self.kanban_1, inventory.missing_kanban_ids)

    def test_inventory_product(self):
        inventory = self.env["stock.inventory.kanban"].create(
            {"product_ids": [(4, self.product.id)]}
        )
        inventory.start_inventory()
        self.assertIn(self.kanban_1, inventory.kanban_ids)
        self.assertNotIn(self.kanban_3, inventory.kanban_ids)
        self.assertIn(self.kanban_1, inventory.missing_kanban_ids)
        self.assertEqual(inventory.state, "in_progress")
        wizard = (
            self.env["wizard.stock.inventory.kanban"]
            .with_context(default_inventory_kanban_id=inventory.id)
            .create({})
        )
        self.pass_code(wizard, self.kanban_3.name)
        self.assertEqual(wizard.status_state, 1)
        self.pass_code(wizard, self.kanban_1.name)
        self.assertEqual(wizard.status_state, 0)
        self.assertNotIn(self.kanban_1, inventory.missing_kanban_ids)
        self.assertIn(self.kanban_1, inventory.scanned_kanban_ids)
        self.pass_code(wizard, self.kanban_1.name)
        self.assertEqual(wizard.status_state, 1)
        self.assertNotIn(self.kanban_1, inventory.missing_kanban_ids)
        self.assertIn(self.kanban_1, inventory.scanned_kanban_ids)
        inventory.finish_inventory()
        self.assertEqual(inventory.state, "finished")
        inventory.close_inventory()
        self.assertEqual(inventory.state, "closed")

    def test_cancel_inventory(self):
        inventory = self.env["stock.inventory.kanban"].create(
            {"product_ids": [(4, self.product.id)]}
        )
        inventory.start_inventory()
        self.assertIn(self.kanban_1, inventory.kanban_ids)
        self.assertNotIn(self.kanban_3, inventory.kanban_ids)
        self.assertIn(self.kanban_1, inventory.missing_kanban_ids)
        self.assertEqual(inventory.state, "in_progress")
        inventory.cancel()
        self.assertEqual(inventory.state, "cancelled")
        inventory.to_draft()
        self.assertEqual(inventory.state, "draft")
        self.assertFalse(inventory.kanban_ids)
        self.assertFalse(inventory.scanned_kanban_ids)
