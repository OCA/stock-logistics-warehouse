# -*- coding: utf-8 -*-
# Copyright 2015-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestBusinessProductLocation(common.TransactionCase):

    def test_business_product_location(self):
        """ Create a business_product_location bpl with :
                * product_product_34 qty 4
                * product_product_35 qty 3
                * stock_location_stock
            Check product_product_34 as a business_product_location with bpl
            Check product_product_35 as a business_product_location with bpl
            Check stock_location_stock as a business_product_location with bpl
        """
        product_17 = self.env.ref('product.product_product_17')
        product_16 = self.env.ref('product.product_product_16')
        stock_loc = self.env.ref('stock.stock_location_stock')
        bpl = self.env['business.product.location'].create({
            'name': 'Test BPL',
            'product_ids': [
                (0, 0, {'product_id': product_17.id, 'product_qty': 4}),
                (0, 0, {'product_id': product_16.id, 'product_qty': 3})],
            'location_ids': [(4, stock_loc.id)]
        })

        self.assertEqual(
            1,
            len(product_17.business_usage_ids))
        self.assertEqual(
            bpl.id,
            product_17.business_usage_ids[0].business_product_location_id.id)
        self.assertEqual(1, len(product_16.business_usage_ids))
        self.assertEqual(
            bpl.id,
            product_16.business_usage_ids[0].business_product_location_id.id)
        self.assertEqual(bpl.id, stock_loc.business_usage_id.id)
