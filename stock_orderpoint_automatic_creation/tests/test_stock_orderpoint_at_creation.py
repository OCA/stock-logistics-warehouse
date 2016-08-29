# -*- coding: utf-8 -*-
# (c) 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.tests.common as common
from openerp import exceptions


class TestStockOderpointAutomaticCreation(common.TransactionCase):

    def setUp(self):
        super(TestStockOderpointAutomaticCreation, self).setUp()
        self.wh_orderpoint = self.env['stock.warehouse.orderpoint']
        self.warehouse = self.env['stock.warehouse'].create({
            'name': 'New WH',
            'code': 'NEWWH'
        })
        self.product = self.env['product.product'].create({'name': 'Test',
                                                           'type': 'product'})

    def test_orderpoint_create(self):
        orderpoints = self.wh_orderpoint.search(
            [('product_id', '=', self.product.id)])
        self.assertEqual(len(orderpoints), 0,
                         'Error orderpoint quantity does not match')
        self.env.user.company_id.create_orderpoints = True
        self.product2 = self.env['product.product'].create({'name': 'Test2',
                                                           'type': 'product'})
        orderpoints = self.wh_orderpoint.search(
            [('product_id', '=', self.product2.id)])
        self.assertEqual(len(orderpoints), 2,
                         'Error orderpoint quantity does not match')
        # Check constraint
        with self.assertRaises(exceptions.ValidationError):
            self.env.user.company_id.orderpoint_product_min_qty = -2
