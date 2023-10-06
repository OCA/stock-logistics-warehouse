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
        self._create_stock_quant(10)

    def _create_stock_quant(self, qty):
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "quantity": qty,
            }
        )

    def _create_stock_reservation(self, qty):
        form_reservation = Form(self.env["stock.reservation"])
        form_reservation.product_id = self.product
        form_reservation.product_uom_qty = qty
        form_reservation.location_id = self.warehouse.lot_stock_id
        return form_reservation.save()

    def test_reservation_not_substract(self):
        self.env.company.stock_reserve_substract_forecasted_quantity = False
        self.assertEqual(self.product.virtual_available, 10)
        picking_form = Form(
            self.env["stock.picking"].with_context(
                default_picking_type_id=self.env.ref("stock.picking_type_out").id
            )
        )
        with picking_form.move_ids_without_package.new() as line_form:
            line_form.product_id = self.product
        picking = picking_form.save()
        picking.move_ids_without_package.product_uom_qty = 10
        picking.action_confirm()
        self.assertEqual(self.product.virtual_available, 0)
        reservation_1 = self._create_stock_reservation(10)
        reservation_1.reserve()
        self.assertEqual(self.product.virtual_available, 0)
        reservation_1.release_reserve()
        self.assertEqual(self.product.virtual_available, 0)
        picking.action_cancel()
        self.assertEqual(self.product.virtual_available, 10)

    def test_reservation_and_reservation_release(self):
        reservation_1 = self._create_stock_reservation(6)
        reservation_1.reserve()
        self.assertFalse(reservation_1.picking_id)
        self.assertEqual(self.product.virtual_available, 4)
        reservation_2 = self._create_stock_reservation(1)
        reservation_2.reserve()
        self.assertFalse(reservation_2.picking_id)
        self.assertEqual(self.product.virtual_available, 3)
        reservation_1.release_reserve()
        self.assertEqual(self.product.virtual_available, 9)

    def test_cron_release(self):
        reservation_1 = self._create_stock_reservation(6)
        reservation_1.date_validity = fields.Date.from_string("2021-01-01")
        reservation_1.reserve()
        self.assertFalse(reservation_1.picking_id)
        self.assertEqual(self.product.virtual_available, 4)
        cron = self.env.ref("stock_reserve.ir_cron_release_stock_reservation")
        cron.method_direct_trigger()
        self.assertEqual(self.product.virtual_available, 10)

    def test_cron_reserve(self):
        reservation_1 = self._create_stock_reservation(11)
        reservation_1.reserve()
        self.assertFalse(reservation_1.picking_id)
        self.assertEqual(reservation_1.state, "partially_available")
        self._create_stock_quant(10)
        cron = self.env.ref("stock_reserve.ir_cron_reserve_waiting_confirmed")
        cron.method_direct_trigger()
        self.assertEqual(reservation_1.state, "assigned")
        self.assertEqual(self.product.virtual_available, 9)
