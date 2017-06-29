# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.tests.common as common
from odoo import exceptions


class TestStockOderpointAutomaticCreation(common.TransactionCase):

    def setUp(self):
        super(TestStockOderpointAutomaticCreation, self).setUp()
        self.wh_orderpoint = self.env['stock.warehouse.orderpoint']
        category_obj = self.env['product.category']
        self.category1 = category_obj.create({'name': 'Orderpoint',
                                              'create_orderpoints': 'yes',
                                              'type': 'normal'})
        self.category2 = category_obj.create({'name': 'No_Orderpoint',
                                              'create_orderpoints': 'no',
                                              'type': 'normal'})

    def test_orderpoint_create(self):
        self.env.user.company_id.create_orderpoints = False
        product_obj = self.env['product.product']
        self.product = product_obj.create({'name': 'Test',
                                           'type': 'product'})
        orderpoints = self.wh_orderpoint.search(
            [('product_id', '=', self.product.id)])
        self.assertEqual(len(orderpoints), 0,
                         'Error orderpoint quantity does not match')
        self.product2 = product_obj.create({'name': 'Test2',
                                            'create_orderpoint': 'yes',
                                            'type': 'product'})
        orderpoints2 = self.wh_orderpoint.search(
            [('product_id', '=', self.product2.id)])
        self.assertEqual(len(orderpoints2), 1,
                         'Error orderpoint quantity does not match')
        self.product3 = product_obj.create({'name': 'Test3',
                                            'type': 'product',
                                            'categ_id': self.category1.id})
        orderpoints3 = self.wh_orderpoint.search(
            [('product_id', '=', self.product3.id)])
        self.assertEqual(len(orderpoints3), 1,
                         'Error orderpoint quantity does not match')
        self.env.user.company_id.create_orderpoints = True
        self.warehouse = self.env['stock.warehouse'].create({
            'name': 'New WH',
            'code': 'NEWWH'
        })
        self.product4 = product_obj.create({'name': 'Test4',
                                            'create_orderpoint': 'no',
                                            'type': 'product'})
        orderpoints4 = self.wh_orderpoint.search(
            [('product_id', '=', self.product4.id)])
        self.assertEqual(len(orderpoints4), 0,
                         'Error orderpoint quantity does not match')
        self.product5 = self.env['product.product'].create(
            {'name': 'Test5',
             'type': 'product',
             'categ_id': self.category2.id})
        orderpoints5 = self.wh_orderpoint.search(
            [('product_id', '=', self.product5.id)])
        self.assertEqual(len(orderpoints5), 0,
                         'Error orderpoint quantity does not match')
        self.product6 = self.env['product.product'].create(
            {'name': 'Test6',
             'type': 'product'})
        orderpoints6 = self.wh_orderpoint.search(
            [('product_id', '=', self.product6.id)])
        self.assertEqual(len(orderpoints6), 2,
                         'Error orderpoint quantity does not match')
        # Check constraint
        with self.assertRaises(exceptions.ValidationError):
            self.env.user.company_id.orderpoint_product_min_qty = -2
