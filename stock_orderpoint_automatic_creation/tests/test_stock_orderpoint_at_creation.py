# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo import exceptions


class TestStockOderpointAutomaticCreation(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockOderpointAutomaticCreation, cls).setUpClass()
        cls.wh_orderpoint = cls.env['stock.warehouse.orderpoint']
        category_obj = cls.env['product.category']
        cls.category1 = category_obj.create({
            'name': 'Orderpoint',
            'create_orderpoints': 'yes',
            'type': 'normal',
        })
        cls.category2 = category_obj.create({
            'name': 'No_Orderpoint',
            'create_orderpoints': 'no',
            'type': 'normal',
        })

    def test_orderpoint_create(self):
        # Company set not to create orderpoints
        self.env.user.company_id.create_orderpoints = False
        product_obj = self.env['product.product']
        self.product = product_obj.create({'name': 'Test',
                                           'type': 'product'})
        orderpoints = self.wh_orderpoint.search(
            [('product_id', '=', self.product.id)])
        # Orderpoints are not creatd
        self.assertEqual(len(orderpoints), 0,
                         'Error orderpoint quantity does not match')
        # Product set to create orderpoints
        self.product2 = product_obj.create({'name': 'Test2',
                                            'create_orderpoint': 'yes',
                                            'type': 'product'})
        orderpoints2 = self.wh_orderpoint.search(
            [('product_id', '=', self.product2.id)])
        # Orderpoint is created
        self.assertEqual(len(orderpoints2), 1,
                         'Error orderpoint quantity does not match')
        # Category set to create orderpoint
        self.product3 = product_obj.create({'name': 'Test3',
                                            'type': 'product',
                                            'categ_id': self.category1.id})
        orderpoints3 = self.wh_orderpoint.search(
            [('product_id', '=', self.product3.id)])
        # Orderpoint is created
        self.assertEqual(len(orderpoints3), 1,
                         'Error orderpoint quantity does not match')
        # Company set to create orderpoints
        self.env.user.company_id.create_orderpoints = True
        self.env.user.company_id.orderpoint_product_min_qty = 10.0
        self.env.user.company_id.orderpoint_product_max_qty = 50.0
        # A new warehouse is created. Now we have two in this company.
        self.warehouse = self.env['stock.warehouse'].create({
            'name': 'New WH',
            'code': 'NEWWH'
        })
        # Product set to no create orderpoint
        self.product4 = product_obj.create({'name': 'Test4',
                                            'create_orderpoint': 'no',
                                            'type': 'product'})
        orderpoints4 = self.wh_orderpoint.search(
            [('product_id', '=', self.product4.id)])
        # Orderpoints are not created
        self.assertEqual(len(orderpoints4), 0,
                         'Error orderpoint quantity does not match')
        # Product an category not set to create orderpoints but company yes
        self.product5 = self.env['product.product'].create(
            {'name': 'Test5',
             'type': 'product',
             'categ_id': self.category2.id})
        orderpoints5 = self.wh_orderpoint.search(
            [('product_id', '=', self.product5.id)])
        # Two orderpoints are created
        self.assertEqual(len(orderpoints5), 0,
                         'Error orderpoint quantity does not match')

        for orderpoint in orderpoints5:
            self.assertAlmostEqual(orderpoint.product_max_qty, 50.0)
            self.assertAlmostEqual(orderpoint.product_min_qty, 10.0)

        # Check constraint
        with self.assertRaises(exceptions.ValidationError):
            self.env.user.company_id.orderpoint_product_min_qty = -2.0
