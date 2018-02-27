# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.tools import mute_logger
from odoo.exceptions import ValidationError


class TestStockOrderpointProcureUom(common.TransactionCase):

    def setUp(self):
        super(TestStockOrderpointProcureUom, self).setUp()
        # Refs
        self.vendor = self.env.ref(
            'stock_orderpoint_uom.product_supplierinfo_product_7')

        # Get required Model
        productObj = self.env['product.product']
        self.purchase_model = self.env['purchase.order']
        self.purchase_line_model = self.env['purchase.order.line']
        self.warehouse = self.env.ref('stock.warehouse0')
        self.location_stock = self.env.ref('stock.stock_location_stock')
        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.uom_dozen = self.env.ref('product.product_uom_dozen')
        self.uom_kg = self.env.ref('product.product_uom_kgm')

        self.productA = productObj.create(
            {'name': 'product A',
             'standard_price': 1,
             'type': 'product',
             'uom_id': self.uom_unit.id,
             'default_code': 'A',
             'variant_seller_ids': [(6, 0, [self.vendor.id])],
             })

    def test_stock_orderpoint_procure_uom(self):

        orderpoint = self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': self.warehouse.id,
            'location_id': self.location_stock.id,
            'product_id': self.productA.id,
            'product_max_qty': 24,
            'product_min_qty': 12,
            'product_uom': self.uom_unit.id,
            'procure_uom_id': self.uom_dozen.id,
        })

        self.env['procurement.group'].run_scheduler()
        # As per route configuration, it will create Purchase order
        purchase = self.purchase_model.search(
            [('origin', 'ilike', orderpoint.name)])
        self.assertEquals(len(purchase), 1)
        purchase_line = self.purchase_line_model.search(
            [('orderpoint_id', '=', orderpoint.id),
             ('order_id', '=', purchase.id)])
        self.assertEquals(len(purchase_line), 1)
        self.assertEqual(purchase_line.product_qty, 2.0)

    def test_stock_orderpoint_wrong_uom(self):

        with mute_logger('openerp.sql_db'):
            with self.assertRaises(ValidationError):
                self.env['stock.warehouse.orderpoint'].create({
                    'warehouse_id': self.warehouse.id,
                    'location_id': self.location_stock.id,
                    'product_id': self.productA.id,
                    'product_max_qty': 24,
                    'product_min_qty': 12,
                    'procure_uom_id': self.uom_kg.id,
                })
