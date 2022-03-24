# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo.fields import Datetime
from odoo.tests import Form
from odoo.tests.common import SavepointCase, users


class SaleStockAvailableInfoPopup(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Scratch some seconds from the tracking stuff that we won't need
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.ref("base.user_demo").groups_id += cls.env.ref("stock.group_stock_user")
        cls.product = cls.env["product.product"].create(
            {"name": "Storable product", "type": "product"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "quantity": 40.0,
            }
        )
        picking_form = Form(cls.env["stock.picking"])
        picking_form.picking_type_id = cls.env.ref("stock.picking_type_in")
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = cls.product
            move.product_uom_qty = 5
        picking_form.save().action_assign()
        picking_form = Form(cls.env["stock.picking"])
        picking_form.picking_type_id = cls.env.ref("stock.picking_type_out")
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = cls.product
            move.product_uom_qty = 3
        picking_form.save().action_assign()

    def _create_sale(self):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.partner
        return sale_form

    def _add_sale_line(self, sale_form, product, qty=1):
        with sale_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = qty

    @users("admin", "demo")
    def test_immediately_usable_qty_today(self):
        sale_form = self._create_sale()
        self._add_sale_line(sale_form, self.product)
        sale = sale_form.save()
        self.assertAlmostEqual(
            sale.order_line.immediately_usable_qty_today,
            self.product.immediately_usable_qty,
        )

    @users("admin", "demo")
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
