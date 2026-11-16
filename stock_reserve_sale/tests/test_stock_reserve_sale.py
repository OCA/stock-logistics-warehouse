# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError, ValidationError
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
        cls.env.company.sale_stock_reservation_policy = "always"

    def _create_sale_order(self, quantities):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        for product, quantity in quantities:
            with sale_order_form.order_line.new() as order_line_form:
                order_line_form.product_id = product
                order_line_form.product_uom_qty = quantity
        return sale_order_form.save()

    def _get_reserve_wizard_form(self, sale_order, location):
        wiz_form = Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order",
                active_id=sale_order.id,
                active_ids=sale_order.ids,
            )
        )
        wiz_form.location_id = location
        return wiz_form

    def _reserve_from_location(self, sale_order, location):
        self._get_reserve_wizard_form(sale_order, location).save().button_reserve()

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

    def test_reserve_06_picking_type_from_source_location(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product_1
            order_line_form.product_uom_qty = 3
        so = sale_order_form.save()
        self.assertNotEqual(so.warehouse_id, self.warehouse)
        wiz_form = Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order.line", active_ids=so.order_line.ids
            )
        )
        wiz_form.location_id = self.warehouse.lot_stock_id
        wiz_form.save().button_reserve()
        reservation = so.order_line.reservation_ids
        self.assertEqual(reservation.picking_type_id, self.warehouse.out_type_id)
        self.assertEqual(
            reservation.picking_id.picking_type_id, self.warehouse.out_type_id
        )

    def test_reserve_07_policy_partial(self):
        self.env.company.sale_stock_reservation_policy = "partial"
        so = self._create_sale_order([(self.product_1, 15)])
        self._reserve_from_location(so, self.warehouse.lot_stock_id)
        reservation = so.order_line.reservation_ids
        self.assertEqual(reservation.product_uom_qty, 10)
        self.assertEqual(reservation.state, "assigned")

    def test_reserve_08_policy_full(self):
        self.env.company.sale_stock_reservation_policy = "full"
        so = self._create_sale_order([(self.product_1, 15), (self.product_2, 5)])
        self._reserve_from_location(so, self.warehouse.lot_stock_id)
        line_1 = so.order_line.filtered(lambda line: line.product_id == self.product_1)
        line_2 = so.order_line - line_1
        self.assertFalse(line_1.reservation_ids)
        self.assertEqual(line_2.reservation_ids.product_uom_qty, 5)
        self.assertEqual(line_2.reservation_ids.state, "assigned")

    def test_reserve_09_policy_no_available_stock(self):
        self.env.company.sale_stock_reservation_policy = "partial"
        so = self._create_sale_order([(self.product_1, 3)])
        with self.assertRaises(UserError):
            self._reserve_from_location(so, self.env.ref("stock.stock_location_stock"))
        self.assertFalse(so.order_line.reservation_ids)
        self.assertFalse(
            self.env["stock.picking"].search([("sale_reserve_id", "=", so.id)])
        )

    def test_reserve_10_without_picking(self):
        self.env.company.sale_stock_reservation_picking = False
        so = self._create_sale_order([(self.product_1, 3)])
        self._reserve_from_location(so, self.warehouse.lot_stock_id)
        reservation = so.order_line.reservation_ids
        self.assertFalse(reservation.picking_id)
        self.assertEqual(reservation.picking_type_id, self.warehouse.out_type_id)
        self.assertEqual(reservation.state, "assigned")
        self.assertFalse(
            self.env["stock.picking"].search([("sale_reserve_id", "=", so.id)])
        )
        so.release_all_stock_reservation()
        self.assertEqual(reservation.state, "cancel")

    def test_reserve_11_wizard_lines(self):
        self.env.company.sale_stock_reservation_policy = "partial"
        so = self._create_sale_order([(self.product_1, 15), (self.product_2, 5)])
        wiz_form = self._get_reserve_wizard_form(so, self.warehouse.lot_stock_id)
        self.assertEqual(len(wiz_form.line_ids), 2)
        with wiz_form.line_ids.edit(0) as line_form:
            self.assertEqual(line_form.product_id, self.product_1)
            self.assertEqual(line_form.available_qty, 10)
            self.assertEqual(line_form.quantity, 10)
        with wiz_form.line_ids.edit(1) as line_form:
            self.assertEqual(line_form.quantity, 5)
            line_form.quantity = 2
        wiz_form.save().button_reserve()
        line_1 = so.order_line.filtered(lambda line: line.product_id == self.product_1)
        line_2 = so.order_line - line_1
        self.assertEqual(line_1.reservation_ids.product_uom_qty, 10)
        self.assertEqual(line_2.reservation_ids.product_uom_qty, 2)

    def test_reserve_12_wizard_line_quantity_checks(self):
        so = self._create_sale_order([(self.product_1, 15), (self.product_2, 5)])
        wiz_form = self._get_reserve_wizard_form(so, self.warehouse.lot_stock_id)
        with wiz_form.line_ids.edit(1) as line_form:
            line_form.quantity = 6
        with self.assertRaises(ValidationError):
            wiz_form.save()
        self.env.company.sale_stock_reservation_policy = "partial"
        wiz_form = self._get_reserve_wizard_form(so, self.warehouse.lot_stock_id)
        with wiz_form.line_ids.edit(0) as line_form:
            line_form.quantity = 12
        with self.assertRaises(ValidationError):
            wiz_form.save()
        self.env.company.sale_stock_reservation_policy = "full"
        wiz_form = self._get_reserve_wizard_form(so, self.warehouse.lot_stock_id)
        with wiz_form.line_ids.edit(0) as line_form:
            self.assertEqual(line_form.quantity, 0)
        with wiz_form.line_ids.edit(1) as line_form:
            line_form.quantity = 3
        with self.assertRaises(ValidationError):
            wiz_form.save()

    def test_reserve_13_default_location_from_order_warehouse(self):
        so = self._create_sale_order([(self.product_1, 3)])
        so.warehouse_id = self.warehouse
        wiz_form = Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order", active_id=so.id, active_ids=so.ids
            )
        )
        self.assertEqual(wiz_form.location_id, self.warehouse.lot_stock_id)
        wiz_form = Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order.line", active_ids=so.order_line.ids
            )
        )
        self.assertEqual(wiz_form.location_id, self.warehouse.lot_stock_id)
