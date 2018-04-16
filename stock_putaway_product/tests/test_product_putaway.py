# Copyright 2018 Camptocamp SA
# Copyright 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from lxml import etree


class TestProductPutaway(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.putawayObj = cls.env['product.putaway']
        cls.putaway_per_product = cls.putawayObj.create({
            'name': 'WH - Putaway Per Product',
            'method': 'per_product'
        })

        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.stock_location.putaway_strategy_id = cls.putaway_per_product
        cls.location_shelf1 = cls.env.ref('stock.stock_location_components')

        cls.product_computer = cls.env.ref('product.product_product_3')
        cls.product_ipad = cls.env.ref('product.product_product_4')

        cls.strategyObj = cls.env['stock.product.putaway.strategy']
        cls.product_putaway_strategy_product_4 = cls.strategyObj.create({
            'product_product_id': cls.product_ipad.id,
            'product_tmpl_id': cls.env.ref(
                'product.product_product_4_product_template').id,
            'putaway_id': cls.putaway_per_product.id,
            'fixed_location_id': cls.location_shelf1.id
        })

    # Check if "per_product" is a valid putaway method
    def test_01_putaway_methods(self):
        field_method = self.env['product.putaway']._fields.get('method')
        self.assertIn('per_product', field_method.get_values(self.env))

    def test_02_putway_apply(self):
        self.assertEqual(
            self.putaway_per_product.putaway_apply(self.product_ipad),
            self.location_shelf1)

    def test_03_stock_change_product_qty_default(self):
        wiz_obj = self.env['stock.change.product.qty']
        test_context = {
            'active_model': 'product.product',
            'active_id': self.product_ipad.id,
        }
        wiz_instance = wiz_obj.with_context(test_context).create({
            'product_tmpl_id': self.product_ipad.product_tmpl_id.id
        })
        self.assertEqual(wiz_instance.location_id, self.location_shelf1)

    def test_04_putaway_apply_none(self):
        self.assertFalse(
            self.putaway_per_product.putaway_apply(self.product_computer))

    def test_05_putaway_apply_fixed(self):
        # Test super
        putaway_fixed = self.putawayObj.create({
            'name': 'TEST',
            'method': 'fixed'
        })
        self.assertEqual(
            putaway_fixed.putaway_apply(self.product_computer),
            self.env['stock.location'])

    def test_06_putaway_check_variant(self):
        t_product = self.env.ref(
            'product.product_product_4_product_template')
        self.assertEqual(type(t_product), type(self.env['product.template']))
        p_product = self.env.ref('product.product_product_5')
        self.assertEqual(type(p_product), type(self.env['product.product']))

        view = p_product.fields_view_get()
        product_xml = etree.XML(view['arch'])
        putaway_path = "//field[@name='product_putaway_ids']"
        putaway_field = product_xml.xpath(putaway_path)[0]
        self.assertEqual(
            putaway_field.attrib['context'],
            "{'default_product_tmpl_id': product_tmpl_id,"
            "'default_product_product_id': active_id}")
