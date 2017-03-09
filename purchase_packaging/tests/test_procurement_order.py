# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo.tests.common as common


class TestProcurementOrder(common.TransactionCase):

    def setUp(self):
        """ Create a packagings with uom  product_uom_dozen on
                * product_product_3 (uom is product_uom_unit)
        """
        super(TestProcurementOrder, self).setUp()
        self.product_packaging_3 = self.env['product.packaging'].create(
            {'product_tmpl_id': self.env.ref('product.product_product_3'
                                             ).product_tmpl_id.id,
             'uom_id': self.env.ref('product.product_uom_dozen').id,
             'name': 'Packaging Dozen'})
        self.sp_30 = self.env.ref('product.product_supplierinfo_1')
        self.sp_30.product_tmpl_id = self.product_packaging_3.product_tmpl_id
        self.sp_30.currency_id = self.env.user.company_id.currency_id
        self.product_uom_8 = self.env['product.uom'].create(
            {'category_id': self.env.ref('product.product_uom_categ_unit').id,
             'name': 'COL8',
             'factor_inv': 8,
             'uom_type': 'bigger',
             'rounding': 1.0,
             })
        self.env['purchase.order'].search(
            [("state", "=", "draft")]).button_cancel()

    def test_procurement(self):
        # On supplierinfo set price to 3
        # On supplierinfo set min_qty as 0
        # Create procurement line with rule buy and quantity 17
        # run procurement
        self.env.ref('product.product_product_3').route_ids = [(
            4, self.env.ref("purchase.route_warehouse0_buy").id)]
        self.env.ref('product.product_uom_unit').rounding = 1
        procurement_obj = self.env['procurement.order']

        self.sp_30.min_qty = 0
        self.sp_30.price = 3

        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_3').id,
             'product_qty': 17,
             'product_uom': self.env.ref('product.product_uom_unit').id})
        procurement_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_unit
        # Check product_purchase_qty is 17
        # Check product_qty is 17
        # Check packaging_id is False
        # Check product_uom is product_uom_unit
        # Check price_unit is 3
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(17, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(17, proc1.purchase_line_id.product_qty)
        self.assertFalse(proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(3, proc1.purchase_line_id.price_unit)
        #  Confirm Purchase Order to avoid group
        proc1.purchase_id.button_confirm()

        # Create procurement line with rule buy and quantity 1 dozen
        # run procurement
        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_3').id,
             'product_qty': 1,
             'product_uom': self.env.ref('product.product_uom_dozen').id})
        procurement_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_unit
        # Check product_purchase_qty is 12
        # Check product_qty is 12
        # Check packaging_id is False
        # Check product_uom is product_uom_unit
        # Check price_unit is 3
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(12, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(12, proc1.purchase_line_id.product_qty)
        self.assertFalse(proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(3, proc1.purchase_line_id.price_unit)
        # Confirm Purchase Order to avoid group
        proc1.purchase_id.button_confirm()

        # On supplierinfo set product_uom_8 as min_qty_uom_id
        # Create procurement line with rule buy and quantity 17
        # run procurement
        self.sp_30.min_qty_uom_id = self.product_uom_8

        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_3').id,
             'product_qty': 17,
             'product_uom': self.env.ref('product.product_uom_unit').id})
        procurement_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_8
        # Check product_purchase_qty is 3
        # Check product_qty is 8*3 = 24
        # Check packaging_id is False
        # Check product_uom is product_uom_unit
        # Check price_unit is 3
        self.assertEqual(self.product_uom_8,
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(3, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(24, proc1.purchase_line_id.product_qty)
        self.assertFalse(proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(3, proc1.purchase_line_id.price_unit)
        # Confirm Purchase Order to avoid group
        proc1.purchase_id.button_confirm()

        # Create procurement line with rule buy and quantity 1 dozen
        # run procurement
        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_3').id,
             'product_qty': 1,
             'product_uom': self.env.ref('product.product_uom_dozen').id})
        procurement_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_8
        # Check product_purchase_qty is 2
        # Check product_qty is 8*2 = 16
        # Check packaging_id is False
        # Check product_uom is product_uom_unit
        # Check price_unit is 3
        self.assertEqual(self.product_uom_8,
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(2, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(16, proc1.purchase_line_id.product_qty)
        self.assertFalse(proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(3, proc1.purchase_line_id.price_unit)
        # Confirm Purchase Order to avoid group
        proc1.purchase_id.button_confirm()

        # On supplierinfo set packaging product_packaging_3 (dozen)
        # Create procurement line with rule buy and quantity 17
        # run procurement
        self.sp_30.packaging_id = self.product_packaging_3

        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_3').id,
             'product_qty': 17,
             'product_uom': self.env.ref('product.product_uom_unit').id})
        procurement_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_8
        # Check product_purchase_qty is 1
        # Check product_qty is 8*1 = 8
        # Check packaging_id is product_packaging_3
        # Check product_uom is product_uom_dozen
        # Check price_unit is 3*12 = 36
        self.assertEqual(self.product_uom_8,
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(1, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(8, proc1.purchase_line_id.product_qty)
        self.assertEqual(self.product_packaging_3,
                         proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_dozen'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(3, proc1.purchase_line_id.price_unit)
        # Confirm Purchase Order to avoid group
        proc1.purchase_id.button_confirm()

        # Create procurement line with rule buy and quantity 1 dozen
        # run procurement
        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_3').id,
             'product_qty': 1,
             'product_uom': self.env.ref('product.product_uom_dozen').id})
        procurement_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_8
        # Check product_purchase_qty is 1
        # Check product_qty is 8*1 = 8
        # Check packaging_id is product_packaging_3
        # Check product_uom is product_uom_dozen
        self.assertEqual(self.product_uom_8,
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(1, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(8, proc1.purchase_line_id.product_qty)
        self.assertEqual(self.product_packaging_3,
                         proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_dozen'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(3, proc1.purchase_line_id.price_unit)
        # Confirm Purchase Order to avoid group
        proc1.purchase_id.button_confirm()

        # On supplierinfo set product_uom_unit as min_qty_uom_id
        # Create procurement line with rule buy and quantity 17
        # run procurement
        self.sp_30.min_qty_uom_id = self.env.ref('product.product_uom_unit')

        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_3').id,
             'product_qty': 17,
             'product_uom': self.env.ref('product.product_uom_unit').id})
        procurement_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_unit
        # Check product_purchase_qty is 2
        # Check product_qty is 2
        # Check packaging_id is product_packaging_3
        # Check product_uom is product_uom_dozen
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(2, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(2, proc1.purchase_line_id.product_qty)
        self.assertEqual(self.product_packaging_3,
                         proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_dozen'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(3, proc1.purchase_line_id.price_unit)
        # Confirm Purchase Order to avoid group
        proc1.purchase_id.button_confirm()

        # Create procurement line with rule buy and quantity 1 dozen
        # set purcahse price to 36
        # run procurement
        self.sp_30.price = 36
        proc1 = procurement_obj.create(
            {'name': 'test_procurement',
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'product_id': self.env.ref('product.product_product_3').id,
             'product_qty': 1,
             'product_uom': self.env.ref('product.product_uom_dozen').id})
        procurement_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_unit
        # Check product_purchase_qty is 1
        # Check product_qty is 1
        # Check packaging_id is product_packaging_3
        # Check product_uom is product_uom_dozen
        # Check price_unit is 3*12 = 36
        self.assertEqual(self.env.ref('product.product_uom_unit'),
                         proc1.purchase_line_id.product_purchase_uom_id)
        self.assertEqual(1, proc1.purchase_line_id.product_purchase_qty)
        self.assertEqual(1, proc1.purchase_line_id.product_qty)
        self.assertEqual(self.product_packaging_3,
                         proc1.purchase_line_id.packaging_id)
        self.assertEqual(self.env.ref('product.product_uom_dozen'),
                         proc1.purchase_line_id.product_uom)
        self.assertEqual(36, proc1.purchase_line_id.price_unit)
        proc1.purchase_id.button_confirm()
