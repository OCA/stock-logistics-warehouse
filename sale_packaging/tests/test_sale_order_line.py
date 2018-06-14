# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo.tests.common as common


class TestSaleOrderLine(common.TransactionCase):

    def setUp(self):
        """ Create a packagings with uom  product_uom_dozen on
                * product_product_3 (uom is product_uom_unit)
        """
        super(TestSaleOrderLine, self).setUp()
        self.product_packaging_dozen = self.env['product.packaging'].create({
            'product_tmpl_id': self.env.ref(
                'product.product_product_3').product_tmpl_id.id,
            'uom_id': self.env.ref('product.product_uom_dozen').id,
            'name': 'dozen',
        })
        self.product_packaging_dozen.product_tmpl_id.lst_price = 45

    def test_packaging_change(self):
        """ Create a sale order line with product product_3
            Set product_packaging product_packaging_dozen
                Check product_uom is product_uom_dozen
                Check product_packaging is product_packaging_dozen
                Check price_subtotal is 1*45*12=540
                Check price_unit is 45*12=540
            Update product_uom_qty with 5
                Check price_unit is 45*12=540
                Check price_subtotal is 5*45*12=2700

        """
        so_line = self.env['sale.order.line'].new({
            'order_id': self.env['sale.order'].create({
                'partner_id': self.env.ref('base.res_partner_2').id
            }),
            'product_id': self.env.ref('product.product_product_3'),
        })
        so_line.product_id_change()
        so_line.product_packaging = self.product_packaging_dozen
        so_line._onchange_product_packaging()
        self.assertEqual(so_line.product_uom.id,
                         self.env.ref('product.product_uom_dozen').id)
        self.assertEqual(so_line.product_packaging.id,
                         self.product_packaging_dozen.id)
        self.assertAlmostEqual(so_line.price_unit, 540)
        self.assertAlmostEqual(so_line.price_subtotal, 540)

        so_line.product_uom_qty = 5
        so_line.product_uom_change()
        self.assertAlmostEqual(so_line.price_unit, 540)
        self.assertAlmostEqual(so_line.product_uom_qty, 5)
        self.assertAlmostEqual(so_line.price_subtotal, 2700)
