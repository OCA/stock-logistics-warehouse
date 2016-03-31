# -*- coding: utf-8 -*-
# © 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestProductPutaway(common.TransactionCase):
    # Check if "per_product" is a valid putaway method
    def test_01_putaway_methods(self):
        field_method = self.env[
            'product.putaway']._fields.get('method')
        self.assertIn('per_product', field_method.get_values(self.env))

    def test_02_putway_apply(self):
        putaway_per_product = self.browse_ref(
            'stock_putaway_product.product_putaway_per_product_wh')
        product_ipad = self.browse_ref(
            'product.product_product_4')
        location_shelf1 = self.browse_ref(
            'stock.stock_location_components')

        self.assertEqual(
            self.env['product.putaway'].putaway_apply(
                putaway_per_product, product_ipad),
            location_shelf1.id)

    def test_03_stock_change_product_qty_default(self):
        product_ipad = self.browse_ref(
            'product.product_product_4')
        location_shelf1 = self.browse_ref(
            'stock.stock_location_components')

        wiz_obj = self.env['stock.change.product.qty']

        test_context = {
            'active_model': 'product.product',
            'active_id': product_ipad.id,
        }
        wiz_instance = wiz_obj.with_context(test_context).create({})
        self.assertEqual(
            wiz_instance.location_id,
            location_shelf1)
