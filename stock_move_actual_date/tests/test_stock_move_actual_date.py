# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from freezegun import freeze_time

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
            }
        )

        move = self.env["stock.move"].create(
            {
                "picking_id": receipt.id,
                "name": "10 in",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product_1.id,
                "product_uom_qty": 10.0,
                "price_unit": 10,
                "move_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                            "qty_done": 10.0,
                        },
                    )
                ],
            }
        )
        move._action_confirm()
        move._action_done()
        return receipt, move

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

    @freeze_time("2024-09-20 23:00:00")
    def test_stock_move_without_actual_date_from_picking_or_scrap(self):
        self.env.user.tz = "Asia/Tokyo"
        receipt, move = self.create_picking()
        self.assertEqual(move.actual_date, date(2024, 9, 21))
        self.assertEqual(move.account_move_ids.date, date(2024, 9, 21))
        scrap = self.create_scrap(receipt)
        self.assertEqual(scrap.move_id.actual_date, date(2024, 9, 21))
        self.assertEqual(scrap.move_id.account_move_ids.date, date(2024, 9, 21))
