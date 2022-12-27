# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from freezegun import freeze_time

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockMoveActualDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        product_category = cls.env["product.category"].create(
            {
                "name": "Test Category",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
            }
        )
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "categ_id": product_category.id,
                "standard_price": 100.0,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "type": "product",
                "categ_id": product_category.id,
                "standard_price": 0.0,
            }
        )
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    def create_picking(self, actual_date=False):
        receipt = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "actual_date": actual_date,
                "move_ids": [
                    Command.create(
                        {
                            "name": "10 in",
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                            "product_id": self.product_1.id,
                            "product_uom_qty": 10.0,
                            "move_line_ids": [
                                Command.create(
                                    {
                                        "product_id": self.product_1.id,
                                        "location_id": self.supplier_location.id,
                                        "location_dest_id": self.stock_location.id,
                                        "qty_done": 10.0,
                                    }
                                )
                            ],
                        }
                    )
                ],
            }
        )
        receipt.move_ids._action_confirm()
        receipt.move_ids._action_done()
        return receipt, receipt.move_ids

    def create_scrap(self, receipt, actual_date=False):
        scrap = self.env["stock.scrap"].create(
            {
                "product_id": self.product_1.id,
                "scrap_qty": 2.0,
                "picking_id": receipt.id,
                "actual_date": actual_date,
            }
        )
        scrap.action_validate()
        return scrap

    def test_stock_move_actual_date(self):
        receipt, move = self.create_picking(date(2024, 9, 1))
        self.assertEqual(move.actual_date, date(2024, 9, 1))
        self.assertEqual(move.account_move_ids.date, date(2024, 9, 1))
        receipt.actual_date = date(2024, 8, 1)
        self.assertEqual(move.actual_date, date(2024, 8, 1))
        self.assertEqual(move.account_move_ids.date, date(2024, 8, 1))
        scrap = self.create_scrap(receipt, date(2024, 9, 10))
        self.assertEqual(scrap.move_id.actual_date, date(2024, 9, 10))
        self.assertEqual(scrap.move_id.account_move_ids.date, date(2024, 9, 10))
        scrap.actual_date = date(2024, 8, 11)
        self.assertEqual(scrap.move_id.actual_date, date(2024, 8, 11))
        self.assertEqual(scrap.move_id.account_move_ids.date, date(2024, 8, 11))

    def test_inventory_adjustment_actual_date(self):
        quant = self.env["stock.quant"].create(
            {
                "location_id": self.stock_location.id,
                "product_id": self.product_1.id,
                "inventory_quantity": 10,
                "accounting_date": date(2024, 7, 1),
            }
        )
        quant.action_apply_inventory()
        move = self.env["stock.move"].search(
            [("product_id", "=", self.product_1.id), ("is_inventory", "=", True)],
            limit=1,
        )
        self.assertEqual(move.actual_date, date(2024, 7, 1))
        self.assertEqual(move.account_move_ids.date, date(2024, 7, 1))

    def test_inventory_adjustment_actual_date_with_zero_standard_price(self):
        quant = self.env["stock.quant"].create(
            {
                "location_id": self.stock_location.id,
                "product_id": self.product_2.id,
                "inventory_quantity": 10,
                "accounting_date": date(2025, 3, 1),
            }
        )
        quant.action_apply_inventory()
        move = self.env["stock.move"].search(
            [("product_id", "=", self.product_2.id), ("is_inventory", "=", True)],
            limit=1,
        )
        self.assertEqual(move.actual_date, date(2025, 3, 1))
        self.assertFalse(move.account_move_ids)

    @freeze_time("2025-05-08 23:00:00")
    def test_stock_move_without_actual_date_from_picking_or_scrap(self):
        self.env.user.tz = "Asia/Tokyo"
        receipt, move = self.create_picking()
        self.assertEqual(move.actual_date, date(2025, 5, 9))
        self.assertEqual(move.account_move_ids.date, date(2025, 5, 9))
        scrap = self.create_scrap(receipt)
        self.assertEqual(scrap.move_id.actual_date, date(2025, 5, 9))
        self.assertEqual(scrap.move_id.account_move_ids.date, date(2025, 5, 9))
        valuation_layer = move.stock_valuation_layer_ids
        self.assertEqual(valuation_layer.actual_date, date(2025, 5, 9))
        account_move = valuation_layer.account_move_id
        account_move.button_draft()
        account_move.name = "/"
        account_move.date = "2025-08-31"
        account_move.action_post()
        self.assertEqual(valuation_layer.actual_date, date(2025, 8, 31))

    def test_svl_actual_date_manual_periodic(self):
        # Not using freeze_time() in this test since it cannot be applied to create_date
        # without a hack.
        self.product_1.product_tmpl_id.categ_id.property_valuation = "manual_periodic"
        _, move = self.create_picking()
        valuation_layer = move.stock_valuation_layer_ids
        self.assertEqual(
            valuation_layer.actual_date, valuation_layer.create_date.date()
        )

    def test_fifo_svl_actual_date(self):
        self.product_1.standard_price = 0.0
        _, move = self.create_picking(date(2025, 3, 10))
        svl = move.stock_valuation_layer_ids
        self.assertTrue(svl, "SVL should be created for the product.")
        self.assertFalse(
            svl.account_move_id, "SVL should not have a related account move."
        )
        self.assertEqual(
            svl.actual_date,
            date(2025, 3, 10),
            "SVL accounting date should match the move actual date.",
        )
