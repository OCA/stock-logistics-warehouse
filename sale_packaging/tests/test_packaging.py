# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.tests.common as common


class TestPackaging(common.TransactionCase):

    def setUp(self):
        """ Create a packagings with uom  product_uom_dozen on
                * product_product_34 (uom is product_uom_unit)
        """
        super(TestPackaging, self).setUp()
        self.product_packaging_34 = self.env['product.packaging'].create(
            {'product_tmpl_id': self.env.ref('product.product_product_34'
                                             ).product_tmpl_id.id,
             'uom_id': self.env.ref('product.product_uom_dozen').id})

    def product_change(self, so_line):
        so_line.product_packaging_change(
            [so_line.id], so_line.order_id.pricelist_id.id,
            so_line.product_id.id, qty=so_line.product_uom_qty,
            uom=so_line.product_uom.id,
            partner_id=so_line.order_id.partner_id.id,
            packaging=so_line.product_packaging.id, flag=True)
        vals = so_line.product_id_change(
            pricelist=so_line.order_id.pricelist_id.id,
            product=so_line.product_id.id, qty=so_line.product_uom_qty,
            uom=so_line.product_uom.id,
            partner_id=so_line.order_id.partner_id.id,
            packaging=so_line.product_packaging.id, flag=False)
        so_line.product_uos_qty = vals['value']['product_uos_qty']
        so_line.name = vals['value']['name']
        so_line.th_weight = vals['value']['th_weight']
        so_line.product_uos = vals['value']['product_uos']
        so_line.price_unit = vals['value']['price_unit']
        so_line.tax_id = vals['value']['tax_id']

    def test_packaging_change(self):
        """ Create a sale order line with product product_product_34
            Set product_packaging product_packaging_34
                Check product_uom is product_uom_dozen
                Check product_packaging is product_packaging_34
                Check price_unit is 45*12=540
            Update product_uom_qty with 5
                Check product_uom is product_uom_unit
                Check product_dpackaging is empty
                Check price_unit is 45
            Set product_packaging product_packaging_34
                Check product_uom_qty is 5
                Check product_uom is product_uom_dozen
                Check product_packaging is product_packaging_34
                Check price_unit is 45*12=540
        """
        so_line = self.env['sale.order.line'].create(
            {'order_id': self.env['sale.order'].create(
                {'partner_id': self.env.ref('base.res_partner_2').id}).id,
             'product_id': self.env.ref('product.product_product_34').id})
        so_line.product_id_change_with_wh(
            so_line.order_id.pricelist_id.id,
            so_line.product_id.id, qty=so_line.product_uom_qty, uom=False,
            qty_uos=so_line.product_uos_qty, uos=False, name=so_line.name,
            partner_id=so_line.order_id.partner_id.id, lang=False,
            update_tax=True, date_order=so_line.order_id.date_order,
            packaging=so_line.product_packaging,
            fiscal_position=so_line.order_id.fiscal_position.id,
            flag=False, warehouse_id=so_line.order_id.warehouse_id.id)
        so_line.product_packaging = self.product_packaging_34
        self.product_change(so_line)
        self.assertEqual(so_line.product_uom.id,
                         self.env.ref('product.product_uom_dozen').id)
        self.assertEqual(so_line.product_packaging.id,
                         self.product_packaging_34.id)
        self.assertAlmostEqual(so_line.price_unit, 540)
        so_line.product_uom_qty = 5
        vals = so_line.product_id_change_with_wh(
            so_line.order_id.pricelist_id.id,
            so_line.product_id.id, qty=so_line.product_uom_qty, uom=False,
            qty_uos=so_line.product_uos_qty, uos=False, name=so_line.name,
            partner_id=so_line.order_id.partner_id.id, lang=False,
            update_tax=True, date_order=so_line.order_id.date_order,
            packaging=so_line.product_packaging,
            fiscal_position=so_line.order_id.fiscal_position.id,
            flag=True, warehouse_id=so_line.order_id.warehouse_id.id)
        so_line.product_tmpl_id = vals['value']['product_tmpl_id']
        so_line.product_uos_qty = vals['value']['product_uos_qty']
        so_line.delay = vals['value']['delay']
        so_line.product_uom = vals['value']['product_uom']
        so_line.th_weight = vals['value']['th_weight']
        so_line.product_uos = vals['value']['product_uos']
        so_line.price_unit = vals['value']['price_unit']
        so_line.product_packaging = vals['value']['product_packaging']
        so_line.tax_id = vals['value']['tax_id']
        self.assertEqual(so_line.product_uom.id,
                         self.env.ref('product.product_uom_unit').id)
        self.assertFalse(so_line.product_packaging)
        self.assertAlmostEqual(so_line.price_unit, 45)
        so_line.product_packaging = self.product_packaging_34
        self.product_change(so_line)
        self.assertEqual(so_line.product_uom.id,
                         self.env.ref('product.product_uom_dozen').id)
        self.assertEqual(so_line.product_packaging.id,
                         self.product_packaging_34.id)
        self.assertAlmostEqual(so_line.price_unit, 540)
        self.assertAlmostEqual(so_line.product_uom_qty, 5)
