# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductPutaway(TransactionCase):
    def setUp(self):
        super().setUp()
        self.putawayObj = self.env["product.putaway"]
        self.putawayLineObj = self.env["stock.fixed.putaway.strat"]
        ProductTemplate = self.env["product.template"]
        ProductAttribute = self.env["product.attribute"]
        ProductAttributeValue = self.env["product.attribute.value"]
        TemplateAttributeLine = self.env["product.template.attribute.line"]
        ref = self.env.ref
        self.product_tmpl_chair = ref(
            "product.product_product_11_product_template"
        )
        self.product_product_chair = ref("product.product_product_11")
        self.category_services = ref("product.product_category_3")
        self.putaway_line_1 = ref(
            "stock_putaway_product_form.putaway_strat_1_line_1"
        )
        self.putaway_line_2 = ref(
            "stock_putaway_product_form.putaway_strat_1_line_2"
        )
        self.putaway_line_3 = ref(
            "stock_putaway_product_form.putaway_strat_2_line_1"
        )
        self.putaway_line_4 = ref(
            "stock_putaway_product_form.putaway_strat_2_line_2"
        )

        # Add a product with variants
        self.template = ProductTemplate.create({
            'name': 'Product test',
            'type': 'consu',
        })
        self.size_attribute = ProductAttribute.create({
            'name': 'Test size',
            'sequence': 1,
        })
        self.size_m = ProductAttributeValue.create({
            'name': 'Size M',
            'attribute_id': self.size_attribute.id,
            'sequence': 1,
        })
        self.size_l = ProductAttributeValue.create({
            'name': 'Size L',
            'attribute_id': self.size_attribute.id,
            'sequence': 2,
        })
        self.template_attribute_lines = TemplateAttributeLine.create({
            'product_tmpl_id': self.template.id,
            'attribute_id': self.size_attribute.id,
            'value_ids': [(6, 0, [self.size_m.id, self.size_l.id])],
        })
        self.template.create_variant_ids()

    def test_tmpl_has_putaways_from_products(self):
        self.assertIn(
            self.putaway_line_1,
            self.product_tmpl_chair.product_tmpl_putaway_ids,
        )
        self.putaway_line_1.product_id = self.env["product.product"]
        self.assertNotIn(
            self.putaway_line_1,
            self.product_tmpl_chair.product_tmpl_putaway_ids,
        )

    def test_tmpl_has_putaways_from_category_simple(self):
        self.assertIn(
            self.putaway_line_2,
            self.product_tmpl_chair.product_putaway_categ_ids,
        )
        self.product_tmpl_chair.categ_id = self.category_services
        self.assertNotIn(
            self.putaway_line_2,
            self.product_tmpl_chair.product_putaway_categ_ids,
        )

    def test_tmpl_has_putaways_from_category_parent(self):
        # chair is under category: all/saleable/office
        self.assertIn(
            self.putaway_line_3,
            self.product_tmpl_chair.product_putaway_categ_ids,
        )
        self.assertNotIn(
            self.putaway_line_4,
            self.product_tmpl_chair.product_putaway_categ_ids,
        )

    def test_apply_putaway(self):
        # Create one strategy line for product template and other with a
        # specific variant
        location = self.env.ref('stock.stock_location_shop0')
        location1 = location.copy({
            'name': 'Location test 1',
            'location_id': location.id
        })
        location2 = location.copy({
            'name': 'Location test 2',
            'location_id': location.id
        })
        variant1 = self.template.product_variant_ids[0]
        variant2 = self.template.product_variant_ids[1]
        putaway = self.putawayObj.create({'name': 'Putaway for test'})
        val_list = [
            {
                'putaway_id': putaway.id,
                'product_tmpl_id': self.template.id,
                'fixed_location_id': location1.id,
            },
            {
                'putaway_id': putaway.id,
                'product_id': variant2.id,
                'fixed_location_id': location2.id,
            },
        ]
        self.putawayLineObj.create(val_list)
        location_applied = putaway._get_putaway_rule(
            variant1).fixed_location_id
        self.assertEqual(location_applied, location1)
        location_applied = putaway._get_putaway_rule(
            variant2).fixed_location_id
        self.assertEqual(location_applied, location2)
