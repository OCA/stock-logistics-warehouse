# -*- coding: utf-8 -*-
# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockQuantityChangeReason(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockQuantityChangeReason, cls).setUpClass()

        # MODELS
        cls.product_product_model = cls.env['product.product']
        cls.product_category_model = cls.env['product.category']
        cls.wizard_model = cls.env['stock.change.product.qty']

        # INSTANCES
        cls.category = cls.product_category_model.create({
            'name': 'Physical (test)'})

    def _create_product(self, name):
        return self.product_product_model.create({
            'name': name,
            'categ_id': self.category.id})

    def _product_change_qty(self, product, new_qty, reason):
        wizard = self.wizard_model.create({'product_id': product.id,
                                           'new_quantity': new_qty,
                                           'reason': reason})
        wizard.change_product_qty()

    def test_product_change_qty(self):
        """ Check product quantity update move reason is well set
        """

        # create products
        product2 = self._create_product('product_product_2')
        product3 = self._create_product('product_product_3')
        product4 = self._create_product('product_product_4')
        product5 = self._create_product('product_product_5')
        product6 = self._create_product('product_product_6')

        # update qty on hand and add reason
        self._product_change_qty(product2, 10, 'product_2_reason')
        self._product_change_qty(product3, 0, 'product_3_reason')
        self._product_change_qty(product4, 0, 'product_4_reason')
        self._product_change_qty(product5, 10, 'product_5_reason')
        self._product_change_qty(product6, 0, 'product_6_reason')

        # check stock moves created
        move2 = self.env['stock.move'].search([('product_id', '=',
                                                product2.id)])
        move3 = self.env['stock.move'].search([('product_id', '=',
                                                product3.id)])
        move4 = self.env['stock.move'].search([('product_id', '=',
                                                product4.id)])
        move5 = self.env['stock.move'].search([('product_id', '=',
                                                product5.id)])
        move6 = self.env['stock.move'].search([('product_id', '=',
                                                product6.id)])

        self.assertEqual(move2.origin, 'product_2_reason')
        self.assertFalse(move3)
        self.assertFalse(move4)
        self.assertEqual(move5.origin, 'product_5_reason')
        self.assertFalse(move6)
