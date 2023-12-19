# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form

from odoo.addons.stock_reserve_sale.tests.test_stock_reserve_sale import (
    TestStockReserveSale,
)


class TestStockReserveSaleMRP(TestStockReserveSale):
    def setUp(self):
        super().setUp()
        product_form = Form(self.env["product.product"])
        product_form.name = "KIT Product"
        product_form.type = "product"
        self.kit_product = product_form.save()

        bom_form = Form(self.env["mrp.bom"])
        bom_form.product_tmpl_id = self.kit_product.product_tmpl_id
        bom_form.product_qty = 1.0
        bom_form.type = "phantom"
        with bom_form.bom_line_ids.new() as component_form:
            component_form.product_id = self.product_1
            component_form.product_qty = 1
        with bom_form.bom_line_ids.new() as component_form:
            component_form.product_id = self.product_2
            component_form.product_qty = 1
        self.bom = bom_form.save()

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
        self.assertEquals(self.product_1.virtual_available, 7)
        self.assertEquals(self.product_2.virtual_available, 7)

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
        self.assertEquals(self.product_1.virtual_available, 3)
        self.assertEquals(self.product_2.virtual_available, 7)
