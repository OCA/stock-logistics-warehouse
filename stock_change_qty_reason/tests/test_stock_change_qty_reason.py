# -*- coding: utf-8 -*-
# © 2016  Denis Roussel, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import openerp.tests.common as common


class TestStockQuantityChangeReason(common.TransactionCase):

    def test_product_change_qty(self):
        """ Check product quantity update move reason is well set"""
        wizard_model = self.env['stock.change.product.qty']
        product2 = self.env.ref('product.product_product_37')
        wizard = wizard_model.create({
            'product_id': product2.id,
            'new_quantity': 10,
            'reason': 'product_37_reason',
        })
        move2 = self.env['stock.move'].search(
            [('product_id', '=', product2.id)], limit=1, order='id desc'
        )
        self.assertEqual(move2.origin, 'product_37_reason')
