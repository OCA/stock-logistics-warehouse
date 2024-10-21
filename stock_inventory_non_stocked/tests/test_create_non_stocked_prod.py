# Copyright 2024 Ivan Perez <iperez@coninpe.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestCreateNonStockedProd(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_inventory = cls.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "location_ids": [
                    (6, 0, [cls.env.ref("stock.stock_location_stock").id])
                ],
            }
        )
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )

    def test_create_non_stocked_products(self):
        self.stock_inventory.create_non_stocked = True
        self.stock_inventory.product_selection = "all"
        self.stock_inventory._get_quants(self.stock_inventory.location_ids)
        self.assertTrue(
            self.env["stock.quant"].search(
                [("product_id", "=", self.product_template.product_variant_id.id)]
            )
        )

    def test_create_non_stocked_products_manual(self):
        self.stock_inventory.create_non_stocked = True
        self.stock_inventory.product_selection = "manual"
        self.stock_inventory.product_ids = self.product_template.product_variant_id
        self.stock_inventory._get_quants(self.stock_inventory.location_ids)
        self.assertTrue(
            self.env["stock.quant"].search(
                [("product_id", "=", self.product_template.product_variant_id.id)]
            )
        )

    def test_create_non_stocked_products_category(self):
        self.stock_inventory.create_non_stocked = True
        self.stock_inventory.product_selection = "category"
        self.stock_inventory.category_id = self.env.ref("product.product_category_all")
        self.stock_inventory._get_quants(self.stock_inventory.location_ids)
        self.assertTrue(
            self.env["stock.quant"].search(
                [("product_id", "=", self.product_template.product_variant_id.id)]
            )
        )

    def test_create_non_stocked_products_domain(self):
        self.stock_inventory.create_non_stocked = True
        self.stock_inventory.product_selection = "domain"
        self.stock_inventory.product_domain = "[('name', '=', 'Test Product')]"
        self.stock_inventory._get_quants(self.stock_inventory.location_ids)
        self.assertTrue(
            self.env["stock.quant"].search(
                [("product_id", "=", self.product_template.product_variant_id.id)]
            )
        )

    def test_create_non_stocked_products_with_lots(self):
        lot = self.env["stock.lot"].create(
            {
                "name": "Test Lot",
                "product_id": self.product_template.product_variant_id.id,
                "company_id": self.env.company.id,
            }
        )
        self.product_template.product_variant_id.tracking = "lot"
        self.stock_inventory.create_non_stocked = True
        self.stock_inventory.product_selection = "one"
        self.stock_inventory.product_ids = self.product_template.product_variant_id
        self.stock_inventory._get_quants(self.stock_inventory.location_ids)
        self.assertTrue(
            self.env["stock.quant"].search(
                [("product_id", "=", self.product_template.product_variant_id.id)]
            )
        )
        self.assertEqual(
            self.env["stock.quant"]
            .search([("product_id", "=", self.product_template.product_variant_id.id)])
            .lot_id,
            lot,
        )

    def test_create_non_stocked_products_with_multiple_lots(self):
        lot1 = self.env["stock.lot"].create(
            {
                "name": "Test Lot 1",
                "product_id": self.product_template.product_variant_id.id,
                "company_id": self.env.company.id,
            }
        )
        lot2 = self.env["stock.lot"].create(
            {
                "name": "Test Lot 2",
                "product_id": self.product_template.product_variant_id.id,
                "company_id": self.env.company.id,
            }
        )
        self.product_template.product_variant_id.tracking = "lot"
        self.stock_inventory.create_non_stocked = True
        self.stock_inventory.product_selection = "one"
        self.stock_inventory.product_ids = self.product_template.product_variant_id
        self.stock_inventory._get_quants(self.stock_inventory.location_ids)
        self.assertTrue(
            self.env["stock.quant"].search(
                [("product_id", "=", self.product_template.product_variant_id.id)]
            )
        )
        quants = self.env["stock.quant"].search(
            [("product_id", "=", self.product_template.product_variant_id.id)]
        )
        for quant in quants:
            self.assertIn(quant.lot_id, [lot1, lot2])

    def test_create_non_stocked_products_with_multiple_locations(self):
        location1 = self.env["stock.location"].create(
            {
                "name": "Test Location 1",
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        location2 = self.env["stock.location"].create(
            {
                "name": "Test Location 2",
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        self.stock_inventory.location_ids = [(4, location1.id), (4, location2.id)]
        self.stock_inventory.create_non_stocked = True
        self.stock_inventory.product_selection = "all"
        self.stock_inventory._get_quants(self.stock_inventory.location_ids)
        self.assertTrue(
            self.env["stock.quant"].search(
                [("product_id", "=", self.product_template.product_variant_id.id)]
            )
        )
        self.assertTrue(
            self.env["stock.quant"]
            .search(
                [
                    ("product_id", "=", self.product_template.product_variant_id.id),
                    ("location_id", "=", location1.id),
                ]
            )
            .location_id,
        )
        self.assertTrue(
            self.env["stock.quant"]
            .search(
                [
                    ("product_id", "=", self.product_template.product_variant_id.id),
                    ("location_id", "=", location2.id),
                ]
            )
            .location_id,
        )
