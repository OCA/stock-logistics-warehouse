# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo.addons.stock_account.tests.test_stockvaluation import TestStockValuation


class TestStockValuation(TestStockValuation):
    def setUp(self):
        super(TestStockValuation, self).setUp()

    def test_stock_picking_actual_date(self):
        self.product1.categ_id.property_cost_method = "fifo"
        actual_date = date.today() + timedelta(days=1)
        receipt = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "actual_date": actual_date,
            }
        )

        move = self.env["stock.move"].create(
            {
                "picking_id": receipt.id,
                "name": "10 in",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product1.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
                "price_unit": 10,
                "move_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
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
        self.assertEqual(move.actual_date, actual_date)
        self.assertEqual(
            move.stock_valuation_layer_ids.account_move_id.date, actual_date
        )
