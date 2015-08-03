# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.tests.common as common


class TestBusinessProductLocation(common.TransactionCase):

    def setUp(self):
        super(TestBusinessProductLocation, self).setUp()

    def test_business_product_location(self):
        """ Create a business_product_location bpl with :
                * product_product_34 qty 4
                * product_product_35 qty 3
                * stock_location_stock
            Check product_product_34 as a business_product_location with bpl
            Check product_product_35 as a business_product_location with bpl
            Check stock_location_stock as a business_product_location with bpl
        """
        bpl = self.env['business.product.location'].create(
            {'name': 'Test BPL',
             'product_ids': [
                 (0, 0, {'product_id': self.env.ref(
                     'product.product_product_34').id, 'product_qty': 4}),
                 (0, 0, {'product_id': self.env.ref(
                     'product.product_product_35').id, 'product_qty': 3})],
             'location_ids': [(4,
                               self.env.ref('stock.stock_location_stock').id)]
             })

        self.assertEqual(
            1,
            len(self.env.ref('product.product_product_34').business_usage_ids))
        self.assertEqual(
            bpl.id,
            self.env.ref('product.product_product_34'
                         ).business_usage_ids[
                0].business_product_location_id.id)
        self.assertEqual(
            1,
            len(self.env.ref('product.product_product_35').business_usage_ids))
        self.assertEqual(
            bpl.id,
            self.env.ref('product.product_product_35'
                         ).business_usage_ids[
                0].business_product_location_id.id)
        self.assertEqual(
            bpl.id,
            self.env.ref('stock.stock_location_stock').business_usage_id.id)
