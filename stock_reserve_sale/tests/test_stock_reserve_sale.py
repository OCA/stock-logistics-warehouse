# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests import Form, common


class TestStockReserveSale(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner_form = Form(cls.env["res.partner"])
        partner_form.name = "Test partner"
        partner_form.country_id = cls.env.ref("base.es")
        cls.partner = partner_form.save()
        warehouse_form = Form(cls.env["stock.warehouse"])
        warehouse_form.name = "Test warehouse"
        warehouse_form.code = "TEST"
        cls.warehouse = warehouse_form.save()
        cls.product_1 = cls.env["product.product"].create(
            [{"name": "Test Product 1", "type": "product"}]
        )
        cls.product_2 = cls.env["product.product"].create(
            [{"name": "Test Product 2", "type": "product"}]
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product_1.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product_2.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )

    def test_reserve_01_tree_reserve_release(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product_1
            order_line_form.product_uom_qty = 3
        so = sale_order_form.save()
        wiz = Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order.line", active_ids=so.order_line.ids
            )
        ).save()
        wiz.button_reserve()
        self.assertEqual(self.product_1.virtual_available, 7)
        so.order_line.release_stock_reservation()
        self.assertEqual(self.product_1.virtual_available, 10)

    def test_reserve_02_all_form_reserve_release(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product_1
            order_line_form.product_uom_qty = 3
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product_2
            order_line_form.product_uom_qty = 5
        so = sale_order_form.save()
        wiz = Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order", active_id=so.id, active_ids=so.ids
            )
        ).save()
        wiz.button_reserve()
        self.assertEqual(self.product_1.virtual_available, 7)
        self.assertEqual(self.product_2.virtual_available, 5)
        so.release_all_stock_reservation()
        self.assertEqual(self.product_1.virtual_available, 10)
        self.assertEqual(self.product_2.virtual_available, 10)

    def test_reserve_03_confirm_order_release(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product_1
            order_line_form.product_uom_qty = 3
        so = sale_order_form.save()
        wiz = Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order.line", active_ids=so.order_line.ids
            )
        ).save()
        wiz.button_reserve()
        self.assertEqual(self.product_1.virtual_available, 7)
        so.action_confirm()
        cancelled_reservation = self.env["stock.reservation"].search(
            [("product_id", "=", self.product_1.id), ("state", "=", "cancel")]
        )
        self.assertEqual(len(cancelled_reservation), 1)
        self.assertEqual(self.product_1.virtual_available, 7)

    def test_reserve_04_cancel_order_release(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product_1
            order_line_form.product_uom_qty = 3
        so = sale_order_form.save()
        wiz = Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order.line", active_ids=so.order_line.ids
            )
        ).save()
        wiz.button_reserve()
        self.assertEqual(self.product_1.virtual_available, 7)
        so.action_cancel()
        cancelled_reservation = self.env["stock.reservation"].search(
            [("product_id", "=", self.product_1.id), ("state", "=", "cancel")]
        )
        self.assertEqual(len(cancelled_reservation), 1)
        self.assertEqual(self.product_1.virtual_available, 10)

    def test_reserve_05_unlink_order(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product_1
            order_line_form.product_uom_qty = 3
        so = sale_order_form.save()
        wiz = Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order.line", active_ids=so.order_line.ids
            )
        ).save()
        wiz.button_reserve()
        with self.assertRaises(UserError):
            so.unlink()
        with self.assertRaises(UserError):
            so.order_line.unlink()
