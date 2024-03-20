# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo.addons.stock_account.tests.test_stockvaluation import TestStockValuation


class TestStockValuation(TestStockValuation):
    def setUp(self):
        super(TestStockValuation, self).setUp()
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
                "standard_price": 100.00,
            }
        )
        self.product.categ_id.property_valuation = "real_time"

    def test_stock_picking_accounting_date(self):
        accounting_date = date.today() + timedelta(days=1)
        receipt = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "accounting_date": accounting_date,
            }
        )

        move = self.env["stock.move"].create(
            {
                "picking_id": receipt.id,
                "name": "10 in",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
                "price_unit": 10,
                "move_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                            "product_uom_id": self.uom_unit.id,
                            "qty_done": 10.0,
                        },
                    )
                ],
            }
        )
        move._action_confirm()
        move._action_done()
        self.assertEqual(
            move.stock_valuation_layer_ids.account_move_id.date, accounting_date
        )

    def test_inventory_adjustment_accounting_date(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 100
        )
        inventory_quant = self.env["stock.quant"].search(
            [
                ("location_id", "=", self.stock_location.id),
                ("product_id", "=", self.product.id),
            ]
        )
        inventory_quant.inventory_quantity = 200.00
        accounting_date = date.today() + timedelta(days=3)
        inventory_quant.accounting_date = accounting_date
        inventory_quant.action_apply_inventory()
        move = self.env["stock.move"].search(
            [("product_id", "=", self.product.id), ("is_inventory", "=", True)],
            limit=1,
        )
        self.assertEqual(
            move.stock_valuation_layer_ids.account_move_id.date, accounting_date
        )
