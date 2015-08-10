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
        self.sp_30 = self.env.ref('product.product_supplierinfo_30')
        self.product_uom_8 = self.env['product.uom'].create(
            {'category_id': self.env.ref('product.product_uom_categ_unit').id,
             'name': 'COL8',
             'factor_inv': 8,
             'uom_type': 'bigger',
             'rounding': 1.0,
             })

    def test_supplierinfo_product_uom(self):
        """ Check product_uom of product_supplierinfo_30 is product_uom_unit
            Set packaging_id product_packaging_34 on product_supplierinfo_30
            Check product_uom of product_supplierinfo_30 is product_uom_dozen
        """
        self.assertEqual(self.sp_30.product_uom.id,
                         self.env.ref('product.product_uom_unit').id)
        self.sp_30.packaging_id = self.product_packaging_34
        self.assertEqual(self.sp_30.product_uom.id,
                         self.env.ref('product.product_uom_dozen').id)

    def test_po_line(self):
        """ On supplierinfo set product_uom_8 as min_qty_uom_id
            On supplierinfo set 2 as min_qty
            Create purchase order line with product product_product_34
            Check packaging_id is product_packaging_34
            Check product_purchase_uom_id is product_uom_8
            Check product_purchase_qty is 2
            Check product_qty is 8*2 = 16
            Check price_unit is 12*38 = 456
            Check product_uom is product_uom_dozen
            Confirm po
            Check stock move packaging is product_packaging_34
            Check stock move product_uom is product_uom_dozen
            Check stock move product_qty is 16
        """
        self.sp_30.min_qty_uom_id = self.product_uom_8
        self.sp_30.min_qty = 2
        self.sp_30.packaging_id = self.product_packaging_34

        po = self.env['purchase.order'].create(
            {'partner_id': self.env.ref('base.res_partner_16').id,
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'pricelist_id': self.env.ref('purchase.list0').id
             })

        vals = self.env['purchase.order.line'].onchange_product_id(
            [],
            po.pricelist_id.id, self.env.ref('product.product_product_34').id,
            0, False, po.partner_id.id, date_order=po.date_order,
            fiscal_position_id=po.fiscal_position.id, date_planned=False,
            name=False, price_unit=False, state=po.state)
        vals['value']['order_id'] = po.id
        vals['value']['product_id'] = self.env.ref(
            'product.product_product_34').id
        po_line = self.env['purchase.order.line'].create(vals['value'])
        self.assertEqual(po_line.packaging_id.id,
                         self.product_packaging_34.id)
        self.assertEqual(po_line.product_purchase_uom_id.id,
                         self.product_uom_8.id)
        self.assertAlmostEqual(po_line.product_purchase_qty, 2)
        self.assertAlmostEqual(po_line.product_qty, 16)
        self.assertAlmostEqual(po_line.price_unit, 456)
        self.assertEqual(po_line.product_uom.id,
                         self.env.ref('product.product_uom_dozen').id)
        po.signal_workflow('purchase_confirm')
        sm = po.picking_ids[0].move_lines[0]
        self.assertEqual(sm.product_packaging.id,
                         self.product_packaging_34.id)
        self.assertEqual(sm.product_uom.id,
                         self.env.ref('product.product_uom_dozen').id)
        self.assertAlmostEqual(sm.product_uom_qty, 16)

    def test_procurement(self):
        """ On product set sale_price to 3
            On supplierinfo set min_qty as 0
            Create procurement line with rule buy and quantity 17
            run procurement
            Check product_purchase_uom_id is product_uom_unit
            Check product_purchase_qty is 17
            Check product_qty is 17
            Check packaging_id is False
            Check product_uom is product_uom_unit
            Check price_unit is 3
            Confirm Purchase Order to avoid group
            Create procurement line with rule buy and quantity 1 dozen
            run procurement
            Check product_purchase_uom_id is product_uom_unit
            Check product_purchase_qty is 12
            Check product_qty is 12
            Check packaging_id is False
            Check product_uom is product_uom_unit
            Check price_unit is 3
            Confirm Purchase Order to avoid group
            On supplierinfo set product_uom_8 as min_qty_uom_id
            Create procurement line with rule buy and quantity 17
            run procurement
            Check product_purchase_uom_id is product_uom_8
            Check product_purchase_qty is 3
            Check product_qty is 8*3 = 24
            Check packaging_id is False
            Check product_uom is product_uom_unit
            Check price_unit is 3
            Confirm Purchase Order to avoid group
            Create procurement line with rule buy and quantity 1 dozen
            run procurement
            Check product_purchase_uom_id is product_uom_8
            Check product_purchase_qty is 2
            Check product_qty is 8*2 = 16
            Check packaging_id is False
            Check product_uom is product_uom_unit
            Check price_unit is 3
            Confirm Purchase Order to avoid group
            On supplierinfo set packaging product_packaging_34 (dozen)
            Create procurement line with rule buy and quantity 17
            run procurement
            Check product_purchase_uom_id is product_uom_8
            Check product_purchase_qty is 1
            Check product_qty is 8*1 = 8
            Check packaging_id is product_packaging_34
            Check product_uom is product_uom_dozen
            Check price_unit is 3*12 = 36
            Confirm Purchase Order to avoid group
            Create procurement line with rule buy and quantity 1 dozen
            run procurement
            Check product_purchase_uom_id is product_uom_8
            Check product_purchase_qty is 1
            Check product_qty is 8*1 = 8
            Check packaging_id is product_packaging_34
            Check product_uom is product_uom_dozen
            Check price_unit is 3*12 = 36
            Confirm Purchase Order to avoid group
            On supplierinfo set product_uom_unit as min_qty_uom_id
            Create procurement line with rule buy and quantity 17
            run procurement
            Check product_purchase_uom_id is product_uom_unit
            Check product_purchase_qty is 2
            Check product_qty is 2
            Check packaging_id is product_packaging_34
            Check product_uom is product_uom_dozen
            Check price_unit is 3*12 = 36
            Confirm Purchase Order to avoid group
            Create procurement line with rule buy and quantity 1 dozen
            run procurement
            Check product_purchase_uom_id is product_uom_unit
            Check product_purchase_qty is 1
            Check product_qty is 1
            Check packaging_id is product_packaging_34
            Check product_uom is product_uom_dozen
            Check price_unit is 3*12 = 36
            Confirm Purchase Order to avoid group
        """
        self.env.ref('product.product_product_34').route_ids = [(
            4, self.env.ref("purchase.route_warehouse0_buy").id)]
        self.env.ref('product.product_product_34').standard_price = 3
        self.env.ref('product.product_uom_unit').rounding = 1
        procurement_obj = self.env['procurement.order']

        self.sp_30.min_qty = 0

        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_34').id,
             'product_qty': 17,
             'product_uom': self.env.ref('product.product_uom_unit').id})
        procurement_obj.run_scheduler()
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(17, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(17, proc1.purchase_line_id.product_qty)
        self.assertFalse(proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_uom)
        proc1.purchase_id.signal_workflow('purchase_confirm')

        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_34').id,
             'product_qty': 1,
             'product_uom': self.env.ref('product.product_uom_dozen').id})
        procurement_obj.run_scheduler()
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(12, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(12, proc1.purchase_line_id.product_qty)
        self.assertFalse(proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(3, proc1.purchase_line_id.price_unit)
        proc1.purchase_id.signal_workflow('purchase_confirm')

        self.sp_30.min_qty_uom_id = self.product_uom_8

        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_34').id,
             'product_qty': 17,
             'product_uom': self.env.ref('product.product_uom_unit').id})
        procurement_obj.run_scheduler()
        self.assertEqual(self.product_uom_8,
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(3, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(24, proc1.purchase_line_id.product_qty)
        self.assertFalse(proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(3, proc1.purchase_line_id.price_unit)
        proc1.purchase_id.signal_workflow('purchase_confirm')

        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_34').id,
             'product_qty': 1,
             'product_uom': self.env.ref('product.product_uom_dozen').id})
        procurement_obj.run_scheduler()
        self.assertEqual(self.product_uom_8,
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(2, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(16, proc1.purchase_line_id.product_qty)
        self.assertFalse(proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(3, proc1.purchase_line_id.price_unit)
        proc1.purchase_id.signal_workflow('purchase_confirm')

        self.sp_30.packaging_id = self.product_packaging_34

        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_34').id,
             'product_qty': 17,
             'product_uom': self.env.ref('product.product_uom_unit').id})
        procurement_obj.run_scheduler()
        self.assertEqual(self.product_uom_8,
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(1, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(8, proc1.purchase_line_id.product_qty)
        self.assertEqual(self.product_packaging_34,
                         proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_dozen'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(36, proc1.purchase_line_id.price_unit)
        proc1.purchase_id.signal_workflow('purchase_confirm')

        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_34').id,
             'product_qty': 1,
             'product_uom': self.env.ref('product.product_uom_dozen').id})
        procurement_obj.run_scheduler()
        self.assertEqual(self.product_uom_8,
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(1, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(8, proc1.purchase_line_id.product_qty)
        self.assertEqual(self.product_packaging_34,
                         proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_dozen'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(36, proc1.purchase_line_id.price_unit)
        proc1.purchase_id.signal_workflow('purchase_confirm')

        self.sp_30.min_qty_uom_id = self.env.ref('product.product_uom_unit')

        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_34').id,
             'product_qty': 17,
             'product_uom': self.env.ref('product.product_uom_unit').id})
        procurement_obj.run_scheduler()
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(2, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(2, proc1.purchase_line_id.product_qty)
        self.assertEqual(self.product_packaging_34,
                         proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_dozen'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(36, proc1.purchase_line_id.price_unit)
        proc1.purchase_id.signal_workflow('purchase_confirm')

        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_34').id,
             'product_qty': 1,
             'product_uom': self.env.ref('product.product_uom_dozen').id})
        procurement_obj.run_scheduler()
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(1, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(1, proc1.purchase_line_id.product_qty)
        self.assertEqual(self.product_packaging_34,
                         proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_dozen'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(36, proc1.purchase_line_id.price_unit)
        proc1.purchase_id.signal_workflow('purchase_confirm')
