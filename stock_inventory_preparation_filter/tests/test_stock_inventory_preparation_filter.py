# Copyright 2015 AvanzOSC - Oihane Crucelaegi
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2020 Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


@common.tagged("-at_install", "post_install")
class TestStockInventoryPreparationFilterCategories(common.TransactionCase):
    def setUp(self):
        super(TestStockInventoryPreparationFilterCategories, self).setUp()
        self.inventory_model = self.env["stock.inventory"]
        self.location = self.env.ref("stock.stock_location_stock")
        self.Product = self.env["product.product"]
        self.Category = self.env["product.category"]
        # Create some categories
        self.category = self.Category.create({"name": "Category for inventory"})
        self.category2 = self.Category.create({"name": "Category for inventory 2"})
        # Create some products in the category
        self.product1 = self.Product.create(
            {
                "name": "Product for inventory 1",
                "type": "product",
                "categ_id": self.category.id,
                "default_code": "PROD1-TEST",
            }
        )
        self.product2 = self.Product.create(
            {
                "name": "Product for inventory 2",
                "type": "product",
                "categ_id": self.category.id,
                "default_code": "PROD2-TEST",
            }
        )
        self.product3 = self.Product.create(
            {
                "name": "Product for inventory 3",
                "type": "product",
                "categ_id": self.category.id,
                "default_code": "PROD3-TEST",
            }
        )
        self.product_lot = self.Product.create(
            {
                "name": "Product for inventory with lots",
                "type": "product",
                "categ_id": self.category2.id,
            }
        )
        self.lot = self.env["stock.production.lot"].create(
            {
                "name": "Lot test",
                "product_id": self.product_lot.id,
                "company_id": self.env.user.company_id.id,
            }
        )
        # Add quants for products to ensure that inventory lines are created
        self.env["stock.quant"].create(
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_id": self.product1.uom_id.id,
                    "location_id": self.location.id,
                    "quantity": 2.0,
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_id": self.product2.uom_id.id,
                    "location_id": self.location.id,
                    "quantity": 2.0,
                },
                {
                    "product_id": self.product3.id,
                    "product_uom_id": self.product3.uom_id.id,
                    "location_id": self.location.id,
                    "quantity": 2.0,
                },
                {
                    "product_id": self.product_lot.id,
                    "product_uom_id": self.product_lot.uom_id.id,
                    "location_id": self.location.id,
                    "quantity": 2.0,
                    "lot_id": self.lot.id,
                },
            ]
        )
        # Add user to lot tracking group
        self.env.user.groups_id = [(4, self.env.ref("stock.group_production_lot").id)]
        # And have some stock in a location
        self.location = self.env["stock.location"].create(
            {"name": "Inventory tests", "usage": "internal"}
        )
        self.test_products = (
            self.product1 + self.product2 + self.product3 + self.product_lot
        )

    def test_inventory_filter(self):
        # Filter all products
        inventory = self.inventory_model.create(
            {"name": "Inventory test", "filter": "products"}
        )
        inventory.action_start()
        self.assertTrue(self.test_products <= inventory.line_ids.mapped("product_id"))
        # Filter by categories
        inventory.action_cancel_draft()
        inventory.update(
            {"filter": "categories", "categ_ids": [(6, 0, [self.category.id])]}
        )
        inventory.action_start()
        self.assertEqual(len(inventory.line_ids), 3)
        # Filter by lots
        inventory.action_cancel_draft()
        inventory.update({"filter": "lots", "lot_ids": [(6, 0, self.lot.ids)]})
        inventory.action_start()
        self.assertEqual(len(inventory.line_ids), 1)

    def test_inventory_domain_filter(self):
        inventory = self.inventory_model.create(
            {
                "name": "Domain inventory",
                "filter": "domain",
                "product_domain": [("id", "=", self.product1.id)],
            }
        )
        inventory.action_start()
        self.assertEqual(len(inventory.line_ids), 1)
        line1 = inventory.line_ids[0]
        self.assertEqual(line1.product_id, self.product1)
        self.assertEqual(line1.theoretical_qty, 2.0)
