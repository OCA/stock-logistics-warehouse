# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockValuationLayer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_category = cls.env["product.category"].create(
            {
                "name": "Test Category FIFO",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "categ_id": product_category.id,
            }
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    def test_fifo_svl_accounting_date(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.stock_location.id,
                "actual_date": date(2025, 3, 10),
                "move_ids": [
                    Command.create(
                        {
                            "name": "Test Move",
                            "product_id": self.product.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.env.ref(
                                "stock.stock_location_suppliers"
                            ).id,
                            "location_dest_id": self.stock_location.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        for move_line in picking.move_line_ids:
            move_line.qty_done = 10
        picking.button_validate()
        svl = picking.move_ids.stock_valuation_layer_ids
        self.assertTrue(svl, "SVL should be created for the product.")
        self.assertFalse(
            svl.account_move_id, "SVL should not have a related account move."
        )
        self.assertEqual(
            svl.accounting_date,
            date(2025, 3, 10),
            "SVL accounting date should match the move actual date.",
        )
