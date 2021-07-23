# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import Form, common


class TestStockReserve(common.TransactionCase):
    def setUp(self):
        super().setUp()
        warehouse_form = Form(self.env["stock.warehouse"])
        warehouse_form.name = "Test warehouse"
        warehouse_form.code = "TEST"
        self.warehouse = warehouse_form.save()
        product_form = Form(self.env["product.product"])
        product_form.name = "Test Product"
        product_form.type = "product"
        self.product = product_form.save()
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )

    def test_reservation_and_reservation_release(self):
        form_reservation_1 = Form(self.env["stock.reservation"])
        form_reservation_1.product_id = self.product
        form_reservation_1.product_uom_qty = 6
        form_reservation_1.location_id = self.warehouse.lot_stock_id
        reservation_1 = form_reservation_1.save()
        reservation_1.reserve()
        self.assertEquals(self.product.virtual_available, 4)
        form_reservation_2 = Form(self.env["stock.reservation"])
        form_reservation_2.product_id = self.product
        form_reservation_2.product_uom_qty = 1
        form_reservation_2.location_id = self.warehouse.lot_stock_id
        reservation_2 = form_reservation_2.save()
        reservation_2.reserve()
        self.assertEquals(self.product.virtual_available, 3)
        reservation_1.release_reserve()
        self.assertEquals(self.product.virtual_available, 9)

    def test_cron_release(self):
        form_reservation_1 = Form(self.env["stock.reservation"])
        form_reservation_1.product_id = self.product
        form_reservation_1.product_uom_qty = 6
        form_reservation_1.location_id = self.warehouse.lot_stock_id
        form_reservation_1.date_validity = fields.Date.from_string("2021-01-01")
        reservation_1 = form_reservation_1.save()
        reservation_1.reserve()
        self.assertEquals(self.product.virtual_available, 4)
        cron = self.env.ref("stock_reserve.ir_cron_release_stock_reservation")
        cron.method_direct_trigger()
        self.assertEquals(self.product.virtual_available, 10)

    def test_cron_reserve(self):
        form_reservation_1 = Form(self.env["stock.reservation"])
        form_reservation_1.product_id = self.product
        form_reservation_1.product_uom_qty = 11
        form_reservation_1.location_id = self.warehouse.lot_stock_id
        reservation_1 = form_reservation_1.save()
        reservation_1.reserve()
        self.assertEquals(reservation_1.state, "partially_available")
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )
        cron = self.env.ref("stock_reserve.ir_cron_reserve_waiting_confirmed")
        cron.method_direct_trigger()
        self.assertEquals(reservation_1.state, "assigned")
        self.assertEquals(self.product.virtual_available, 9)
