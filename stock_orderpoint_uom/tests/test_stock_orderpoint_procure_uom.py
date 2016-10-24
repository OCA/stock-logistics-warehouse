# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common
from openerp.tools import mute_logger
from openerp.exceptions import ValidationError


class TestStockOrderpointProcureUom(common.TransactionCase):

    def setUp(self):
        super(TestStockOrderpointProcureUom, self).setUp()
        productObj = self.env['product.product']
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
             })

    def test_stock_orderpoint_procure_uom(self):

        self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': self.warehouse.id,
            'location_id': self.location_stock.id,
            'product_id': self.productA.id,
            'product_max_qty': 24,
            'product_min_qty': 12,
            'procure_uom_id': self.uom_dozen.id,
        })

        sched = self.env['procurement.order']
        sched.run_scheduler()
        proc = sched.search([('product_id', '=', self.productA.id)])
        self.assertEqual(proc.product_uom, self.uom_dozen)
        self.assertEqual(proc.product_qty, 2)

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
