# -*- coding: utf-8 -*-
# © 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


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
            putaway_per_product.putaway_apply(product_ipad),
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
        wiz_instance = wiz_obj.with_context(test_context).create(
            {'product_tmpl_id': product_ipad.product_tmpl_id.id})
        self.assertEqual(
            wiz_instance.location_id,
            location_shelf1)

    def test_04_putaway_apply_none(self):
        putaway_per_product = self.browse_ref(
            'stock_putaway_product.product_putaway_per_product_wh')
        product_computer = self.browse_ref(
            'product.product_product_3')
        self.assertEqual(
            putaway_per_product.putaway_apply(product_computer),
            False)

    def test_05_putaway_apply_fixed(self):
        # Test super
        vals = {'name': 'TEST',
                'method': 'fixed'
                }
        putaway_fixed = self.env['product.putaway'].create(vals)
        product_computer = self.browse_ref(
            'product.product_product_3')
        self.assertEqual(
            putaway_fixed.putaway_apply(product_computer),
            self.env['stock.location'])

    def test_06_putaway_check_variant(self):
        t_product = self.browse_ref(
            'product.product_product_4_product_template')
        self.assertEqual(False,
                         t_product.is_product_variant,
                         'The product is not a template one')
        p_product = self.browse_ref(
            'product.product_product_5')
        self.assertEqual(True,
                         p_product.is_product_variant,
                         'The product is not a variant one')
