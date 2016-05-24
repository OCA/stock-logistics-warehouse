# -*- coding: utf-8 -*-
# © 2016  Denis Roussel, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestStockQuantityChangeReason(common.TransactionCase):

    def _product_change_qty(self, product, new_qty, reason):
        wizard_model = self.env['stock.change.product.qty']
        wizard = wizard_model.create({'product_id': product.id,
                                      'new_quantity': new_qty,
                                      'reason': reason})
        wizard.change_product_qty()

    def test_product_change_qty(self):
        """ Check product quantity update move reason is well set
        """

        # set product in each period
        product2 = self.env.ref('product.product_product_37')
        product3 = self.env.ref('product.product_product_38')
        product4 = self.env.ref('product.product_product_39')
        product5 = self.env.ref('product.product_product_40')
        product6 = self.env.ref('product.product_product_41')

        self._product_change_qty(product2, 10, 'product_37_reason')
        self._product_change_qty(product3, 0, 'product_38_reason')
        self._product_change_qty(product4, 0, 'product_39_reason')
        self._product_change_qty(product5, 10, 'product_40_reason')
        self._product_change_qty(product6, 0, 'product_41_reason')

        move2 = self.env['stock.move'].search([('product_id', '=',
                                                product2.id)], limit=1,
                                              order='id desc')
        move3 = self.env['stock.move'].search([('product_id', '=',
                                                product3.id)],
                                              limit=1, order='id desc')
        move4 = self.env['stock.move'].search([('product_id', '=',
                                                product4.id)],
                                              limit=1, order='id desc')
        move5 = self.env['stock.move'].search([('product_id', '=',
                                                product5.id)],
                                              limit=1, order='id desc')
        move6 = self.env['stock.move'].search([('product_id', '=',
                                                product6.id)],
                                              limit=1, order='id desc')

        self.assertEqual(move2.origin, 'product_37_reason')
        self.assertFalse(move3)
        self.assertFalse(move4)
        self.assertEqual(move5.origin, 'product_40_reason')
        self.assertFalse(move6)
