# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase


class TestProductSecondaryUnit(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.product_uom_kg = cls.env.ref('product.product_uom_kgm')
        cls.product_uom_unit = cls.env.ref('product.product_uom_unit')
        ProductAttribute = cls.env['product.attribute']
        ProductAttributeValue = cls.env['product.attribute.value']
        cls.attribute_color = ProductAttribute.create({'name': 'test_color'})
        cls.attribute_value_white = ProductAttributeValue.create({
            'name': 'test_white',
            'attribute_id': cls.attribute_color.id,
        })
        cls.attribute_value_black = ProductAttributeValue.create({
            'name': 'test_black',
            'attribute_id': cls.attribute_color.id,
        })
        Product = cls.env['product.product']
        cls.product_template = cls.env['product.template'].create({
            'name': 'test',
            'uom_id': cls.product_uom_kg.id,
            'uom_po_id': cls.product_uom_kg.id,
            'type': 'product',
            'secondary_uom_ids': [
                (0, 0, {
                    'code': 'A',
                    'name': 'unit-700',
                    'uom_id': cls.product_uom_unit.id,
                    'factor': 0.5,
                }),
                (0, 0, {
                    'code': 'B',
                    'name': 'unit-900',
                    'uom_id': cls.product_uom_unit.id,
                    'factor': 0.9,
                }),
            ],
            'attribute_line_ids': [(0, 0, {
                'attribute_id': cls.attribute_color.id,
            })],
        })
        cls.product_white = Product.create({
            'product_tmpl_id': cls.product_template.id,
            'attribute_value_ids': [(6, 0, [cls.attribute_value_white.id])],
        })
        cls.product_black = Product.create({
            'product_tmpl_id': cls.product_template.id,
            'attribute_value_ids': [(6, 0, [cls.attribute_value_black.id])],
        })
        secondary_unit = cls.env['product.secondary.unit'].search([
            ('product_tmpl_id', '=', cls.product_template.id),
        ], limit=1)
        cls.product_template.write({
            'sale_secondary_uom_id': secondary_unit.id,
            'stock_secondary_uom_id': secondary_unit.id,
        })
        StockQuant = cls.env['stock.quant']
        cls.quant_white = StockQuant.create({
            'product_id': cls.product_white.id,
            'location_id': cls.warehouse.lot_stock_id.id,
            'quantity': 10.0,
        })
        cls.quant_black = StockQuant.create({
            'product_id': cls.product_black.id,
            'location_id': cls.warehouse.lot_stock_id.id,
            'quantity': 10.0,
        })

    def test_stock_secondary_unit_template(self):
        self.assertEqual(
            self.product_template.secondary_unit_qty_available, 40.0)

    def test_stock_secondary_unit_variant(self):
        for variant in self.product_template.product_variant_ids.filtered(
                'attribute_value_ids'):
            self.assertEqual(variant.secondary_unit_qty_available, 20)
