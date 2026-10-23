# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.fields import Command
from odoo.tests import Form

from odoo.addons.stock_reserve_sale.tests.test_stock_reserve_sale import (
    TestStockReserveSale,
)


class TestStockReserveSaleMRP(TestStockReserveSale):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kit_product = cls.env["product.product"].create(
            {"name": "KIT Product", "type": "product"}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.kit_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "phantom",
                "bom_line_ids": [
                    Command.create({"product_id": cls.product_1.id, "product_qty": 1}),
                    Command.create({"product_id": cls.product_2.id, "product_qty": 1}),
                ],
            }
        )

    def _get_reservation(self, reservations, product):
        return reservations.filtered(lambda res: res.product_id == product)

    def test_reserve_01_kit_bom(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.kit_product
            order_line_form.product_uom_qty = 3
        so = sale_order_form.save()
        wiz = Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order", active_id=so.id, active_ids=so.ids
            )
        ).save()
        wiz.button_reserve()
        self.assertEqual(self.product_1.virtual_available, 7)
        self.assertEqual(self.product_2.virtual_available, 7)

    def test_reserve_02_mixed_products(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.kit_product
            order_line_form.product_uom_qty = 3
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product_1
            order_line_form.product_uom_qty = 4
        so = sale_order_form.save()
        wiz = Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order", active_id=so.id, active_ids=so.ids
            )
        ).save()
        wiz.button_reserve()
        self.assertEqual(self.product_1.virtual_available, 3)
        self.assertEqual(self.product_2.virtual_available, 7)

    def test_reserve_03_kit_components(self):
        so = self._create_sale_order([(self.kit_product, 3)])
        self._reserve_from_location(so, self.warehouse.lot_stock_id)
        reservations = so.order_line.reservation_ids
        self.assertEqual(len(reservations), 2)
        self.assertEqual(
            reservations.mapped("product_id"), self.product_1 | self.product_2
        )
        self.assertEqual(reservations.mapped("product_uom_qty"), [3.0, 3.0])
        self.assertEqual(
            reservations.mapped("product_uom"), self.bom.bom_line_ids.product_uom_id
        )
        self.assertEqual(set(reservations.mapped("state")), {"assigned"})
        self.assertEqual(
            reservations.mapped("picking_type_id"), self.warehouse.out_type_id
        )
        self.assertEqual(len(reservations.mapped("picking_id")), 1)
        so.release_all_stock_reservation()
        self.assertEqual(set(reservations.mapped("state")), {"cancel"})

    def test_reserve_04_kit_policy_partial(self):
        self.env.company.sale_stock_reservation_policy = "partial"
        self.bom.bom_line_ids.filtered(
            lambda line: line.product_id == self.product_2
        ).product_qty = 4
        so = self._create_sale_order([(self.kit_product, 3)])
        wiz_form = self._get_reserve_wizard_form(so, self.warehouse.lot_stock_id)
        with wiz_form.line_ids.edit(0) as line_form:
            self.assertEqual(line_form.available_qty, 2)
            self.assertEqual(line_form.quantity, 2)
        wiz_form.save().button_reserve()
        reservations = so.order_line.reservation_ids
        self.assertEqual(
            self._get_reservation(reservations, self.product_1).product_uom_qty, 2
        )
        self.assertEqual(
            self._get_reservation(reservations, self.product_2).product_uom_qty, 8
        )
        self.assertEqual(set(reservations.mapped("state")), {"assigned"})

    def test_reserve_05_kit_policy_full(self):
        self.env.company.sale_stock_reservation_policy = "full"
        so = self._create_sale_order([(self.kit_product, 15), (self.product_1, 5)])
        wiz_form = self._get_reserve_wizard_form(so, self.warehouse.lot_stock_id)
        with wiz_form.line_ids.edit(0) as line_form:
            self.assertEqual(line_form.product_id, self.kit_product)
            self.assertEqual(line_form.available_qty, 10)
            self.assertEqual(line_form.quantity, 0)
        wiz_form.save().button_reserve()
        kit_line = so.order_line.filtered(
            lambda line: line.product_id == self.kit_product
        )
        self.assertFalse(kit_line.reservation_ids)
        self.assertEqual((so.order_line - kit_line).reservation_ids.product_uom_qty, 5)

    def test_reserve_06_kit_all_lines_reserved(self):
        so = self._create_sale_order([(self.kit_product, 3), (self.product_1, 2)])
        kit_line = so.order_line.filtered(
            lambda line: line.product_id == self.kit_product
        )
        Form(
            self.env["sale.stock.reserve"].with_context(
                active_model="sale.order.line", active_ids=kit_line.ids
            )
        ).save().button_reserve()
        self.assertEqual(so.reserves_count, 2)
        self.assertFalse(so.all_lines_reserved)
        self._reserve_from_location(so, self.warehouse.lot_stock_id)
        self.assertEqual(so.reserves_count, 3)
        self.assertTrue(so.all_lines_reserved)
