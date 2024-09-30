# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestStockInventoryPreparationFilterPos(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.location = self.env.ref("stock.stock_location_stock")
        ppo = self.env["product.product"]
        pcateg_id = self.env["product.category"].create({"name": "Test1"}).id
        self.pos_categ1 = self.env["pos.category"].create({"name": "Test POS Categ"})
        self.pos_categ2 = self.env["pos.category"].create(
            {"name": "Test POS Categ2", "parent_id": self.pos_categ1.id}
        )
        # Create products
        self.product1 = ppo.create(
            {
                "name": "Product POS test1",
                "type": "product",
                "categ_id": pcateg_id,
                "pos_categ_id": self.pos_categ1.id,
            }
        )
        self.product2 = ppo.create(
            {
                "name": "Product POS test2",
                "type": "product",
                "categ_id": pcateg_id,
                "pos_categ_id": self.pos_categ1.id,
            }
        )
        self.product3 = ppo.create(
            {
                "name": "Product POS test3",
                "type": "product",
                "categ_id": pcateg_id,
                "pos_categ_id": self.pos_categ2.id,
            }
        )

        # Add stock levels for these products
        self.env["stock.quant"].create(
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_id": self.product1.uom_id.id,
                    "location_id": self.location.id,
                    "quantity": 42.0,
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_id": self.product2.uom_id.id,
                    "location_id": self.location.id,
                    "quantity": 43.0,
                },
                {
                    "product_id": self.product3.id,
                    "product_uom_id": self.product3.uom_id.id,
                    "location_id": self.location.id,
                    "quantity": 44.0,
                },
            ]
        )

    def test_inventory_filter_pos(self):
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test POS filter",
                "filter": "pos_categories",
                "pos_categ_ids": [(6, 0, self.pos_categ1.ids)],
            }
        )
        inventory.action_start()
        # We make sure that the products of children categs are also included
        self.assertEqual(len(inventory.product_ids), 3)
        self.assertEqual(len(inventory.line_ids), 3)
        inventory.action_cancel_draft()
