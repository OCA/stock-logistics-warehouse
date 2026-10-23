# © 2023 FactorLibre - Hugo Córdoba <hugo.cordoba@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form

from .common import TestReserveExtraPickingCommon


class TestReserveExtraPicking(TestReserveExtraPickingCommon):
    def test_00_reserves_count(self):
        """
        This test checks that the calculation of the reserved lines counter is correct
        """
        wiz = Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order.line",
                active_ids=self.sale_order.order_line.ids,
            )
        ).save()
        wiz.button_reserve()
        self.assertEqual(self.sale_order.reserves_count, 2)
        self.sale_order.order_line[0].release_stock_reservation()
        self.assertEqual(self.sale_order.reserves_count, 1)
        self.sale_order.order_line[1].release_stock_reservation()
        self.assertEqual(self.sale_order.reserves_count, 0)

    def test_01_all_lines_reserved(self):
        line_1, line_2 = self.sale_order.order_line
        wiz = self.env["sale.stock.reserve"].create({})
        vals = wiz._prepare_stock_reservation(line_1)
        self.env["stock.reservation"].create([vals, vals])
        self.assertEqual(self.sale_order.reserves_count, 2)
        self.assertFalse(self.sale_order.all_lines_reserved)
        self.env["stock.reservation"].create(wiz._prepare_stock_reservation(line_2))
        self.assertEqual(self.sale_order.reserves_count, 3)
        self.assertTrue(self.sale_order.all_lines_reserved)
        line_1.release_stock_reservation()
        self.assertFalse(self.sale_order.all_lines_reserved)

    def test_reserve_stock_reservation(self):
        self.context = {
            "active_id": self.sale_order.id,
            "active_ids": [self.sale_order.id],
            "active_model": "sale.order",
        }
        self.sale_stock_reserve = (
            self.env["sale.stock.reserve"].with_context(**self.context).create({})
        )
        self.sale_stock_reserve.button_reserve()
        self.context_2 = {
            "active_id": self.sale_order_2.id,
            "active_ids": [self.sale_order_2.id],
            "active_model": "sale.order",
        }
        self.sale_stock_reserve = (
            self.env["sale.stock.reserve"].with_context(**self.context_2).create({})
        )
        self.sale_stock_reserve.button_reserve()
        self.picking = self.env["stock.picking"].search(
            [("sale_reserve_id", "=", self.sale_order.id)]
        )
        self.picking_2 = self.env["stock.picking"].search(
            [("sale_reserve_id", "=", self.sale_order_2.id)]
        )
        self.assertTrue(self.picking)
        self.assertTrue(self.picking_2)
        self.assertNotEqual(self.picking, self.picking_2)
