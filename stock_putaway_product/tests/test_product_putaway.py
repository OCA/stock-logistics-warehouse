# -*- coding: utf-8 -*-

from openerp.tests import common


class TestProductPutaway(common.TransactionCase):
    # Check if "per_product" is a valid putaway method
    def test_01_putaway_methods(self):
        selection_field_items = [item[0] for item in self.env[
            'product.putaway'].method.get_values()]
        self.assertIn('per_product', selection_field_items)

    def test_02_putway_apply(self):
        putaway_per_product = self.browse_ref(
            'stock_putaway_product.product_putaway_per_product')
        product_ipad = self.browse_ref(
            'product.product_product_4')
        location_shelf1 = self.browse_ref(
            'stock.stock_location_components')

        self.assertEqual(
            self.env['product.putaway'].putaway_apply(
                putaway_per_product, product_ipad),
            location_shelf1)

    def test_03_stock_change_product_qty_default(self):
        product_ipad = self.browse_ref(
            'product.product_product_4')
        location_shelf1 = self.browse_ref(
            'stock.stock_location_components')

        wiz_obj = self.env['stock.change.product.qty']

        fields = [f[0] for f in wiz_obj._fields]
        test_context = {
            'active_model': 'product.product',
            'active_id': product_ipad.id,
        }

        res = wiz_obj.with_context(test_context).default_get(fields)
        self.assertEqual(
            res.get('location_id'),
            location_shelf1.id)
