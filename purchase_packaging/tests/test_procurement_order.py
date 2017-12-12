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

    def test_procurement_from_orderpoint_draft_po(self):
        # Define a multiple of 12 on supplier info
        # Trigger a stock minimum rule of 10 PC
        # A purchase line with 12 PC should be generated
        # Change the stock minimum to 11 PC
        # The purchase quantity should remains 12
        # Change the stock minimum to 13 PC
        # The purchase quantity should increase up to 24
        warehouse = self.env.ref('stock.warehouse0')
        product = self.env.ref('product.product_product_3')
        product.route_ids = [(
            4, self.env.ref("purchase.route_warehouse0_buy").id)]
        self.env.ref('product.product_uom_dozen').rounding = 1
        procurement_obj = self.env['procurement.order']

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.env.ref('product.product_uom_dozen')

        orderpoint = self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': warehouse.id,
            'location_id': warehouse.lot_stock_id.id,
            'product_id': product.id,
            'product_min_qty': 10,
            'product_max_qty': 10,
        })
        procurement_obj.run_scheduler()
        proc = procurement_obj.search([('orderpoint_id', '=', orderpoint.id)])
        self.assertEqual(len(proc), 1)
        self.assertTrue(proc.purchase_line_id)
        self.assertEqual(proc.purchase_line_id.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 11
        orderpoint.product_max_qty = 11

        procurement_obj.run_scheduler()
        procs = procurement_obj.search([('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(procs)
        self.assertEqual(len(procs), 1)

        # change order_point level and rerun
        orderpoint.product_min_qty = 13
        orderpoint.product_max_qty = 13

        procurement_obj.run_scheduler()
        procs = procurement_obj.search([('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(procs)
        self.assertEqual(len(procs), 2)

        for proc in procs:
            self.assertTrue(proc.purchase_line_id)
            self.assertEqual(proc.purchase_line_id.product_qty, 24)

    def test_procurement_from_orderpoint_sent_po(self):
        # Define a multiple of 12 on supplier info
        # Trigger a stock minimum rule of 10 PC
        # A purchase line with 12 PC should be generated
        # Send the purchase order
        # Change the stock minimum to 11 PC
        # No new purchase should be generated
        # Change the stock minimum to 13 PC
        # A new purchase should be generated
        warehouse = self.env.ref('stock.warehouse0')
        product = self.env.ref('product.product_product_3')
        product.route_ids = [(
            4, self.env.ref("purchase.route_warehouse0_buy").id)]
        self.env.ref('product.product_uom_dozen').rounding = 1
        procurement_obj = self.env['procurement.order']

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.env.ref('product.product_uom_dozen')

        orderpoint = self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': warehouse.id,
            'location_id': warehouse.lot_stock_id.id,
            'product_id': product.id,
            'product_min_qty': 10,
            'product_max_qty': 10,
        })
        procurement_obj.run_scheduler()
        proc = procurement_obj.search([('orderpoint_id', '=', orderpoint.id)])
        self.assertEqual(len(proc), 1)
        self.assertTrue(proc.purchase_line_id)
        self.assertEqual(proc.purchase_line_id.product_qty, 12)

        proc.purchase_line_id.order_id.write({'state': 'sent'})

        # change order_point level and rerun
        orderpoint.product_min_qty = 11
        orderpoint.product_max_qty = 11

        procurement_obj.run_scheduler()
        proc = procurement_obj.search([('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(proc)
        self.assertEqual(len(proc), 1)
        self.assertEqual(proc.purchase_line_id.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 13
        orderpoint.product_max_qty = 13

        procurement_obj.run_scheduler()
        procs = procurement_obj.search([('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(procs)
        self.assertEqual(len(procs), 2)

        for proc in procs:
            self.assertTrue(proc.purchase_line_id)
            self.assertEqual(proc.purchase_line_id.product_qty, 12)

    def test_procurement_from_orderpoint_to_approve_po(self):
        # Define a multiple of 12 on supplier info
        # Trigger a stock minimum rule of 10 PC
        # A purchase line with 12 PC should be generated
        # Set the purchase order to approve
        # Change the stock minimum to 11 PC
        # No new purchase should be generated
        # Change the stock minimum to 13 PC
        # A new purchase should be generated
        warehouse = self.env.ref('stock.warehouse0')
        product = self.env.ref('product.product_product_3')
        product.route_ids = [(
            4, self.env.ref("purchase.route_warehouse0_buy").id)]
        self.env.ref('product.product_uom_dozen').rounding = 1
        procurement_obj = self.env['procurement.order']

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.env.ref('product.product_uom_dozen')

        orderpoint = self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': warehouse.id,
            'location_id': warehouse.lot_stock_id.id,
            'product_id': product.id,
            'product_min_qty': 10,
            'product_max_qty': 10,
        })
        procurement_obj.run_scheduler()
        proc = procurement_obj.search([('orderpoint_id', '=', orderpoint.id)])
        self.assertEqual(len(proc), 1)
        self.assertTrue(proc.purchase_line_id)
        self.assertEqual(proc.purchase_line_id.product_qty, 12)

        proc.purchase_line_id.order_id.write({'state': 'to approve'})

        # change order_point level and rerun
        orderpoint.product_min_qty = 11
        orderpoint.product_max_qty = 11

        procurement_obj.run_scheduler()
        proc = procurement_obj.search([('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(proc)
        self.assertEqual(len(proc), 1)
        self.assertEqual(proc.purchase_line_id.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 13
        orderpoint.product_max_qty = 13

        procurement_obj.run_scheduler()
        procs = procurement_obj.search([('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(procs)
        self.assertEqual(len(procs), 2)

        for proc in procs:
            self.assertTrue(proc.purchase_line_id)
            self.assertEqual(proc.purchase_line_id.product_qty, 12)

    def test_procurement_from_orderpoint_confirmed_po(self):
        # Define a multiple of 12 on supplier info
        # Trigger a stock minimum rule of 10 PC
        # A purchase line with 12 PC should be generated
        # Confirm the purchase order
        # Change the stock minimum to 11 PC
        # No new purchase should be generated
        # Change the stock minimum to 13 PC
        # A new purchase should be generated
        warehouse = self.env.ref('stock.warehouse0')
        product = self.env.ref('product.product_product_3')
        product.route_ids = [(
            4, self.env.ref("purchase.route_warehouse0_buy").id)]
        self.env.ref('product.product_uom_dozen').rounding = 1
        procurement_obj = self.env['procurement.order']

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.env.ref('product.product_uom_dozen')

        orderpoint = self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': warehouse.id,
            'location_id': warehouse.lot_stock_id.id,
            'product_id': product.id,
            'product_min_qty': 10,
            'product_max_qty': 10,
        })
        procurement_obj.run_scheduler()
        proc = procurement_obj.search([('orderpoint_id', '=', orderpoint.id)])
        self.assertEqual(len(proc), 1)
        self.assertTrue(proc.purchase_line_id)
        self.assertEqual(proc.purchase_line_id.product_qty, 12)

        proc.purchase_line_id.order_id.button_confirm()

        # change order_point level and rerun
        orderpoint.product_min_qty = 11
        orderpoint.product_max_qty = 11

        procurement_obj.run_scheduler()
        proc = procurement_obj.search([('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(proc)
        self.assertEqual(len(proc), 1)
        self.assertEqual(proc.purchase_line_id.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 13
        orderpoint.product_max_qty = 13

        procurement_obj.run_scheduler()
        procs = procurement_obj.search([('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(procs)
        self.assertEqual(len(procs), 2)

        for proc in procs:
            self.assertTrue(proc.purchase_line_id)
            self.assertEqual(proc.purchase_line_id.product_qty, 12)
