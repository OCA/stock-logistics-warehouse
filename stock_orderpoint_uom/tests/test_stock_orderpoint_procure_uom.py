# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestStockOrderpointProcureUom(common.TransactionCase):

    def test_stock_orderpoont_procure_uom(self):
        super(TestStockOrderpointProcureUom, self).setUp()
        productObj = self.env['product.product']
        warehouse = self.env.ref('stock.warehouse0')
        location_stock = self.env.ref('stock.stock_location_stock')
        uom_unit = self.env.ref('product.product_uom_unit')
        uom_dozen = self.env.ref('product.product_uom_dozen')
        self.company_partner = self.env.ref('base.main_partner')

        productA = productObj.create(
            {'name': 'product A',
             'standard_price': 1,
             'type': 'product',
             'uom_id': uom_unit.id,
             'default_code': 'A',
             })

        self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': warehouse.id,
            'location_id': location_stock.id,
            'product_id': productA.id,
            'product_max_qty': 24,
            'product_min_qty': 12,
            'procure_uom_id': uom_dozen.id,
        })

        sched = self.env['procurement.order']
        sched.run_scheduler()
        proc = sched.search([('product_id', '=', productA.id)])
        self.assertEqual(proc.product_uom, uom_dozen)
        self.assertEqual(proc.product_qty, 2)
