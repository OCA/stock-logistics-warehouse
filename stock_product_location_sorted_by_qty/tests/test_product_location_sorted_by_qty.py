# -*- coding: utf-8 -*-
# Copyright 2018 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestProductLocationSortedByQty(TransactionCase):

    def test_product_location_sorted_by_qty(self):
        product_ipad = self.env.ref(
            'product.product_product_4')
        location_shelf1 = self.browse_ref(
            'stock.stock_location_components')
        location_shelf2 = self.env.ref(
            'stock.stock_location_14')

        wiz_obj = self.env['stock.change.product.qty']

        test_context = {
            'stock_change_product_quantity': True,
            'default_product_id': product_ipad.id,
        }
        # update quantity for ipad in shelf1 location
        wiz_instance1 = wiz_obj.with_context(test_context).create({
            'product_id': product_ipad.id,
            'product_tmpl_id': product_ipad.product_tmpl_id.id,
            'location_id': location_shelf1.id,
            'new_quantity': 12.0
        })
        wiz_instance1.change_product_qty()

        # update quantity for ipad in shelf2 location
        wiz_instance2 = wiz_obj.with_context(test_context).create({
            'product_id': product_ipad.id,
            'product_tmpl_id': product_ipad.product_tmpl_id.id,
            'location_id': location_shelf2.id,
            'new_quantity': 25.0
        })
        wiz_instance2.change_product_qty()
        # create a new wizard to check the order location by quantity
        wiz_instance = wiz_obj.with_context(test_context).create({
            'product_id': product_ipad.id,
            'product_tmpl_id': product_ipad.product_tmpl_id.id,
        })
        name = u''
        args = [('usage', '=', 'internal')]
        operator = 'ilike'
        limit = 100
        res = wiz_instance.location_id.name_search(
            name=name, args=args, operator=operator, limit=limit)

        elm1 = wiz_instance1.location_id.name_get()[0]
        index_elm1 = res.index(elm1)
        elm2 = wiz_instance2.location_id.name_get()[0]
        index_elm2 = res.index(elm2)
        self.assertGreater(index_elm1, index_elm2)
        self.assertEqual(res[index_elm2][1], 'WH/Stock/Shelf 2 (25.0)')
        self.assertEqual(res[index_elm1][1], 'WH/Stock/Shelf 1 (12.0)')
