# Copyright 2022 ForgeFlow S.L
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockInventory(TransactionCase):
    def setUp(self):
        super(TestStockInventory, self).setUp()
        self.quant_model = self.env["stock.quant"]
        self.move_model = self.env["stock.move.line"]
        self.inventory_model = self.env["stock.inventory"]
        self.location_model = self.env["stock.location"]
        self.product_categ = self.env["product.category"].create({"name": "Test Categ"})
        self.product = self.env["product.product"].create(
            {
                "name": "Product 1 test",
                "type": "product",
                "tracking": "lot",
            }
        )
        self.product2 = self.env["product.product"].create(
            {
                "name": "Product 1 test",
                "type": "product",
                "categ_id": self.product_categ.id,
            }
        )
        self.lot_1 = self.env["stock.production.lot"].create(
            {
                "product_id": self.product.id,
                "name": "Lot 1",
                "company_id": self.env.company.id,
            }
        )
        self.lot_2 = self.env["stock.production.lot"].create(
            {
                "product_id": self.product.id,
                "name": "Lot 2",
                "company_id": self.env.company.id,
            }
        )
        self.lot_3 = self.env["stock.production.lot"].create(
            {
                "product_id": self.product.id,
                "name": "Lot 3",
                "company_id": self.env.company.id,
            }
        )
        self.location_src = self.env.ref("stock.stock_location_locations_virtual")
        self.location_dst = self.env.ref("stock.stock_location_customers")

        self.location1 = self.location_model.create(
            {
                "name": "Location 1",
                "usage": "internal",
                "warehouse_id": self.location_src.id,
            }
        )
        self.location2 = self.location_model.create(
            {
                "name": "Location 2",
                "usage": "internal",
                "location_id": self.location_src.id,
            }
        )
        self.location3 = self.location_model.create(
            {
                "name": "Location 3",
                "usage": "internal",
                "location_id": self.location1.id,
            }
        )
        self.quant1 = self.quant_model.sudo().create(
            {
                "product_id": self.product.id,
                "lot_id": self.lot_1.id,
                "quantity": 100.0,
                "location_id": self.location1.id,
            }
        )
        self.quant2 = self.quant_model.sudo().create(
            {
                "product_id": self.product.id,
                "lot_id": self.lot_2.id,
                "quantity": 100.0,
                "location_id": self.location2.id,
            }
        )
        self.quant3 = self.quant_model.sudo().create(
            {
                "product_id": self.product.id,
                "lot_id": self.lot_3.id,
                "quantity": 100.0,
                "location_id": self.location3.id,
            }
        )
        self.quant4 = self.quant_model.sudo().create(
            {
                "product_id": self.product2.id,
                "quantity": 100.0,
                "location_id": self.location3.id,
            }
        )

    def test_01_all_locations(self):
        inventory1 = self.inventory_model.create(
            {
                "name": "Inventory_Test_1",
                "product_selection": "all",
                "location_ids": [self.location1.id],
            }
        )
        inventory1.action_state_to_in_progress()
        inventory2 = self.inventory_model.create(
            {
                "name": "Inventory_Test_2",
                "product_selection": "all",
                "location_ids": [self.location1.id],
            }
        )
        with self.assertRaises(ValidationError), self.cr.savepoint():
            inventory2.action_state_to_in_progress()
        self.assertEqual(inventory1.state, "in_progress")
        self.assertEqual(
            inventory1.stock_quant_ids.ids,
            [self.quant1.id, self.quant3.id, self.quant4.id],
        )
        inventory1.action_state_to_draft()
        self.assertEqual(inventory1.stock_quant_ids.ids, [])
        inventory1.action_state_to_in_progress()
        self.assertEqual(inventory1.count_stock_moves, 0)
        self.assertEqual(inventory1.count_stock_quants, 3)
        self.assertEqual(inventory1.count_stock_quants_string, "3 / 3")
        inventory1.action_view_inventory_adjustment()
        self.quant1.inventory_quantity = 92
        self.quant1.action_apply_inventory()
        inventory1._compute_count_stock_quants()
        inventory1.action_view_stock_moves()
        self.assertEqual(inventory1.count_stock_moves, 1)
        self.assertEqual(inventory1.count_stock_quants, 3)
        self.assertEqual(inventory1.count_stock_quants_string, "2 / 3")
        self.assertEqual(inventory1.stock_move_ids.qty_done, 8)
        self.assertEqual(inventory1.stock_move_ids.product_id.id, self.product.id)
        self.assertEqual(inventory1.stock_move_ids.lot_id.id, self.lot_1.id)
        self.assertEqual(inventory1.stock_move_ids.location_id.id, self.location1.id)
        inventory1.action_state_to_done()

    def test_02_manual_selection(self):
        inventory1 = self.inventory_model.create(
            {
                "name": "Inventory_Test_3",
                "product_selection": "manual",
                "location_ids": [self.location1.id],
                "product_ids": [self.product.id],
            }
        )
        inventory1.action_state_to_in_progress()
        self.assertEqual(inventory1.state, "in_progress")
        self.assertEqual(
            inventory1.stock_quant_ids.ids, [self.quant1.id, self.quant3.id]
        )
        inventory1.action_state_to_draft()
        self.assertEqual(inventory1.stock_quant_ids.ids, [])
        inventory1.action_state_to_in_progress()
        self.assertEqual(inventory1.state, "in_progress")
        self.assertEqual(inventory1.count_stock_moves, 0)
        self.assertEqual(inventory1.count_stock_quants, 2)
        self.assertEqual(inventory1.count_stock_quants_string, "2 / 2")
        inventory1.action_view_inventory_adjustment()
        self.quant3.inventory_quantity = 74
        self.quant3.action_apply_inventory()
        inventory1._compute_count_stock_quants()
        inventory1.action_view_stock_moves()
        self.assertEqual(inventory1.count_stock_moves, 1)
        self.assertEqual(inventory1.count_stock_quants, 2)
        self.assertEqual(inventory1.count_stock_quants_string, "1 / 2")
        self.assertEqual(inventory1.stock_move_ids.qty_done, 26)
        self.assertEqual(inventory1.stock_move_ids.product_id.id, self.product.id)
        self.assertEqual(inventory1.stock_move_ids.lot_id.id, self.lot_3.id)
        self.assertEqual(inventory1.stock_move_ids.location_id.id, self.location3.id)
        self.quant1.inventory_quantity = 65
        self.quant1.action_apply_inventory()
        inventory1._compute_count_stock_quants()
        self.assertEqual(inventory1.count_stock_moves, 2)
        self.assertEqual(inventory1.count_stock_quants, 2)
        self.assertEqual(inventory1.count_stock_quants_string, "0 / 2")
        inventory1.action_state_to_done()

    def test_03_one_selection(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            inventory1 = self.inventory_model.create(
                {
                    "name": "Inventory_Test_5",
                    "product_selection": "one",
                    "location_ids": [self.location1.id],
                    "product_ids": [self.product.id, self.product2.id],
                }
            )
        inventory1 = self.inventory_model.create(
            {
                "name": "Inventory_Test_5",
                "product_selection": "one",
                "location_ids": [self.location1.id],
                "product_ids": [self.product.id],
            }
        )
        inventory1.action_state_to_in_progress()
        inventory1.product_ids = [self.product.id]
        self.assertEqual(
            inventory1.stock_quant_ids.ids, [self.quant1.id, self.quant3.id]
        )
        inventory1.action_state_to_draft()
        self.assertEqual(inventory1.stock_quant_ids.ids, [])
        inventory1.action_state_to_in_progress()
        self.assertEqual(inventory1.state, "in_progress")
        self.assertEqual(inventory1.count_stock_moves, 0)
        self.assertEqual(inventory1.count_stock_quants, 2)
        self.assertEqual(inventory1.count_stock_quants_string, "2 / 2")
        inventory1.action_view_inventory_adjustment()
        self.quant3.inventory_quantity = 74
        self.quant3.action_apply_inventory()
        inventory1._compute_count_stock_quants()
        inventory1.action_view_stock_moves()
        self.assertEqual(inventory1.count_stock_moves, 1)
        self.assertEqual(inventory1.count_stock_quants, 2)
        self.assertEqual(inventory1.count_stock_quants_string, "1 / 2")
        self.assertEqual(inventory1.stock_move_ids.qty_done, 26)
        self.assertEqual(inventory1.stock_move_ids.product_id.id, self.product.id)
        self.assertEqual(inventory1.stock_move_ids.lot_id.id, self.lot_3.id)
        self.assertEqual(inventory1.stock_move_ids.location_id.id, self.location3.id)
        self.quant1.inventory_quantity = 65
        self.quant1.action_apply_inventory()
        inventory1._compute_count_stock_quants()
        self.assertEqual(inventory1.count_stock_moves, 2)
        self.assertEqual(inventory1.count_stock_quants, 2)
        self.assertEqual(inventory1.count_stock_quants_string, "0 / 2")
        inventory1.action_state_to_done()

    def test_04_lot_selection(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            inventory1 = self.inventory_model.create(
                {
                    "name": "Inventory_Test_6",
                    "product_selection": "lot",
                    "location_ids": [self.location1.id],
                    "lot_ids": [self.lot_3.id],
                    "product_ids": [self.product.id, self.product2.id],
                }
            )
        inventory1 = self.inventory_model.create(
            {
                "name": "Inventory_Test_6",
                "product_selection": "lot",
                "location_ids": [self.location1.id],
                "lot_ids": [self.lot_3.id],
                "product_ids": [self.product.id],
            }
        )
        inventory1.product_ids = [self.product.id]
        inventory1.action_state_to_in_progress()
        self.assertEqual(inventory1.stock_quant_ids.ids, [self.quant3.id])
        inventory1.action_state_to_draft()
        self.assertEqual(inventory1.stock_quant_ids.ids, [])
        inventory1.action_state_to_in_progress()
        self.assertEqual(inventory1.state, "in_progress")
        self.assertEqual(inventory1.count_stock_moves, 0)
        self.assertEqual(inventory1.count_stock_quants, 1)
        self.assertEqual(inventory1.count_stock_quants_string, "1 / 1")
        inventory1.action_view_inventory_adjustment()
        self.quant3.inventory_quantity = 74
        self.quant3.action_apply_inventory()
        inventory1._compute_count_stock_quants()
        inventory1.action_view_stock_moves()
        self.assertEqual(inventory1.count_stock_moves, 1)
        self.assertEqual(inventory1.count_stock_quants, 1)
        self.assertEqual(inventory1.count_stock_quants_string, "0 / 1")
        self.assertEqual(inventory1.stock_move_ids.qty_done, 26)
        self.assertEqual(inventory1.stock_move_ids.product_id.id, self.product.id)
        self.assertEqual(inventory1.stock_move_ids.lot_id.id, self.lot_3.id)
        self.assertEqual(inventory1.stock_move_ids.location_id.id, self.location3.id)
        inventory1.action_state_to_done()

    def test_05_category_selection(self):
        inventory1 = self.inventory_model.create(
            {
                "name": "Inventory_Test_7",
                "product_selection": "category",
                "location_ids": [self.location3.id],
                "category_id": self.product_categ.id,
            }
        )
        inventory1.action_state_to_in_progress()
        self.assertEqual(inventory1.stock_quant_ids.ids, [self.quant4.id])
        inventory1.action_state_to_draft()
        self.assertEqual(inventory1.stock_quant_ids.ids, [])
        inventory1.action_state_to_in_progress()
        self.assertEqual(inventory1.state, "in_progress")
        self.assertEqual(inventory1.count_stock_moves, 0)
        self.assertEqual(inventory1.count_stock_quants, 1)
        self.assertEqual(inventory1.count_stock_quants_string, "1 / 1")
        inventory1.action_view_inventory_adjustment()
        self.quant4.inventory_quantity = 74
        self.quant4.action_apply_inventory()
        inventory1._compute_count_stock_quants()
        inventory1.action_view_stock_moves()
        self.assertEqual(inventory1.count_stock_moves, 1)
        self.assertEqual(inventory1.count_stock_quants, 1)
        self.assertEqual(inventory1.count_stock_quants_string, "0 / 1")
        self.assertEqual(inventory1.stock_move_ids.qty_done, 26)
        self.assertEqual(inventory1.stock_move_ids.product_id.id, self.product2.id)
        self.assertEqual(inventory1.stock_move_ids.location_id.id, self.location3.id)
        inventory1.action_state_to_done()
