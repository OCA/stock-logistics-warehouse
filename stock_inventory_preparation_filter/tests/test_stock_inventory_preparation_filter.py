# Copyright 2015 AvanzOSC - Oihane Crucelaegi
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2020 Iván Todorovich
# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


@common.tagged("-at_install", "post_install")
class TestStockInventoryPreparation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inventory_model = cls.env["stock.inventory"]
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.Product = cls.env["product.product"]
        cls.Category = cls.env["product.category"]
        # Create some categories
        cls.category = cls.Category.create({"name": "Category for inventory"})
        cls.category2 = cls.Category.create({"name": "Category for inventory 2"})
        # Create some products in the category
        cls.product1 = cls.Product.create(
            {
                "name": "Product for inventory 1",
                "type": "product",
                "categ_id": cls.category.id,
                "default_code": "PROD1-TEST",
            }
        )
        cls.product2 = cls.Product.create(
            {
                "name": "Product for inventory 2",
                "type": "product",
                "categ_id": cls.category.id,
                "default_code": "PROD2-TEST",
            }
        )
        cls.product3 = cls.Product.create(
            {
                "name": "Product for inventory 3",
                "type": "product",
                "categ_id": cls.category.id,
                "default_code": "PROD3-TEST",
            }
        )
        cls.product_lot = cls.Product.create(
            {
                "name": "Product for inventory with lots",
                "type": "product",
                "categ_id": cls.category2.id,
            }
        )
        cls.lot = cls.env["stock.production.lot"].create(
            {
                "name": "Lot test",
                "product_id": cls.product_lot.id,
                "company_id": cls.env.user.company_id.id,
            }
        )
        # Add quants for products to ensure that inventory lines are created
        cls.env["stock.quant"].create(
            [
                {
                    "product_id": cls.product1.id,
                    "product_uom_id": cls.product1.uom_id.id,
                    "location_id": cls.location.id,
                    "quantity": 2.0,
                },
                {
                    "product_id": cls.product2.id,
                    "product_uom_id": cls.product2.uom_id.id,
                    "location_id": cls.location.id,
                    "quantity": 2.0,
                },
                {
                    "product_id": cls.product3.id,
                    "product_uom_id": cls.product3.uom_id.id,
                    "location_id": cls.location.id,
                    "quantity": 2.0,
                },
                {
                    "product_id": cls.product_lot.id,
                    "product_uom_id": cls.product_lot.uom_id.id,
                    "location_id": cls.location.id,
                    "quantity": 2.0,
                    "lot_id": cls.lot.id,
                },
            ]
        )
        # Add user to lot tracking group
        cls.env.user.groups_id = [(4, cls.env.ref("stock.group_production_lot").id)]
        # And have some stock in a location
        cls.location = cls.env["stock.location"].create(
            {"name": "Inventory tests", "usage": "internal"}
        )
        cls.test_products = cls.product1 + cls.product2 + cls.product3 + cls.product_lot

    def test_inventory_filter(self):
        # Filter all products
        inventory = self.inventory_model.create(
            {
                "name": "Inventory test",
                "product_selection": "all",
                "location_ids": self.env.ref("stock.stock_location_stock"),
            }
        )
        inventory.action_state_to_in_progress()
        self.assertTrue(
            self.test_products <= inventory.stock_quant_ids.mapped("product_id")
        )
        # Filter by categories
        inventory.action_state_to_draft()
        inventory.update(
            {
                "product_selection": "category",
                "category_id": self.category.id,
            }
        )
        inventory.action_state_to_in_progress()
        self.assertEqual(len(inventory.stock_quant_ids), 3)
        # Filter by lots
        inventory.action_state_to_draft()
        inventory.update(
            {
                "product_selection": "lot",
                "lot_ids": self.lot.ids,
                "product_ids": self.product_lot,
            }
        )
        inventory.action_state_to_in_progress()
        self.assertEqual(len(inventory.stock_quant_ids), 1)

    def test_inventory_domain_filter(self):
        inventory = self.inventory_model.create(
            {
                "name": "Domain inventory",
                "product_selection": "domain",
                "product_domain": [("id", "=", self.product1.id)],
                "location_ids": self.env.ref("stock.stock_location_stock"),
            }
        )
        inventory.action_state_to_in_progress()
        self.assertEqual(len(inventory.stock_quant_ids), 1)
        line1 = inventory.stock_quant_ids[0]
        self.assertEqual(line1.product_id, self.product1)
        self.assertEqual(line1.quantity, 2.0)
