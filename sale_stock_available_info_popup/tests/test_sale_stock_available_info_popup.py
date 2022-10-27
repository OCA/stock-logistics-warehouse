# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo.fields import Datetime
from odoo.tests import Form, common, new_test_user
from odoo.tests.common import users


class SaleStockAvailableInfoPopup(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_user = new_test_user(
            cls.env,
            login="sale_user",
            groups="sales_team.group_sale_salesman",
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Storable product", "detailed_type": "product"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "quantity": 40.0,
            }
        )
        picking_in = cls._create_picking(cls, cls.env.ref("stock.picking_type_in"), 5)
        picking_in.action_assign()
        picking_out = cls._create_picking(cls, cls.env.ref("stock.picking_type_out"), 3)
        picking_out.action_assign()

    def _create_picking(self, picking_type, qty):
        picking_form = Form(self.env["stock.picking"])
        picking_form.picking_type_id = picking_type
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.product
            move.product_uom_qty = qty
        return picking_form.save()

    def _create_sale(self):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.partner
        sale_form.user_id = self.sale_user
        return sale_form

    def _add_sale_line(self, sale_form, product, qty=1):
        with sale_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = qty

    @users("admin", "sale_user")
    def test_immediately_usable_qty_today(self):
        sale_form = self._create_sale()
        self._add_sale_line(sale_form, self.product)
        sale = sale_form.save()
        # 42=40-1+3
        self.assertAlmostEqual(sale.order_line.immediately_usable_qty_today, 42)

    @users("admin", "sale_user")
    def test_immediately_usable_qty_today_similar_solines(self):
        """Create a sale order containing three times the same product. The quantity
        available should be different for the 3 lines.
        """
        # Modules like stock_available_inmmediately change the behavior of this field
        # so we have to evaluate their values on the fly
        qty = self.product.immediately_usable_qty
        yesterday = Datetime.now() - timedelta(days=1)
        sale_form = self._create_sale()
        self._add_sale_line(sale_form, self.product, 5)
        self._add_sale_line(sale_form, self.product, 5)
        self._add_sale_line(sale_form, self.product, 5)
        sale = sale_form.save()
        self.assertEqual(
            sale.order_line.mapped("immediately_usable_qty_today"),
            [qty, qty - 5, qty - 10],
        )
        self.product.invalidate_cache()
        qty_yesterday = self.product.with_context(
            to_date=yesterday
        ).immediately_usable_qty
        self.assertFalse(qty == qty_yesterday)
        # Commitment date will affect the computation
        sale.commitment_date = yesterday
        sale.order_line.invalidate_cache()
        self.assertEqual(
            sale.order_line.mapped("immediately_usable_qty_today"),
            [qty_yesterday, qty_yesterday - 5, qty_yesterday - 10],
        )
