# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Tecnativa - Sergio Teruel
# Copyright 2020-2021 Víctor Martínez - Tecnativa

from odoo.tests import common


class TestStockPutawayRule(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.putawayRuleObj = cls.env["stock.putaway.rule"]
        ProductTemplate = cls.env["product.template"]
        ProductAttribute = cls.env["product.attribute"]
        ProductAttributeValue = cls.env["product.attribute.value"]
        TemplateAttributeLine = cls.env["product.template.attribute.line"]
        # Add a product with variants
        cls.template = ProductTemplate.create({"name": "Product test", "type": "consu"})
        cls.size_attribute = ProductAttribute.create(
            {"name": "Test size", "sequence": 1}
        )
        cls.size_m = ProductAttributeValue.create(
            {"name": "Size M", "attribute_id": cls.size_attribute.id, "sequence": 1}
        )
        cls.size_l = ProductAttributeValue.create(
            {"name": "Size L", "attribute_id": cls.size_attribute.id, "sequence": 2}
        )
        cls.size_xl = ProductAttributeValue.create(
            {"name": "Size XL", "attribute_id": cls.size_attribute.id, "sequence": 3}
        )
        cls.template_attribute_lines = TemplateAttributeLine.create(
            {
                "product_tmpl_id": cls.template.id,
                "attribute_id": cls.size_attribute.id,
                "value_ids": [(6, 0, [cls.size_m.id, cls.size_l.id, cls.size_xl.id])],
            }
        )
        cls.template._create_variant_ids()
        cls.view_id = cls.env.ref("stock.stock_putaway_list").id

    def _stock_putaway_rule_product(self, location, product):
        rule = self.putawayRuleObj.create(
            {
                "company_id": location.company_id.id,
                "product_id": product.id,
                "location_in_id": location.id,
                "location_out_id": location.id,
            }
        )
        self.assertEqual(rule.location_in_id, location)
        self.assertEqual(rule.product_tmpl_id, product.product_tmpl_id)
        self.assertEqual(rule.product_id, product)
        return rule

    def _get_product_rules(self, product):
        return self.putawayRuleObj.search(
            product.action_view_related_putaway_rules()["domain"]
        )

    def test_apply_putaway(self):
        # Create one strategy line for product template and other with a
        # specific variant
        location = self.env.ref("stock.stock_location_shop0")
        location1 = location.copy(
            {"name": "Location test 1", "location_id": location.id}
        )
        location2 = location.copy(
            {"name": "Location test 2", "location_id": location.id}
        )
        # Create rule according to product_tmpl_id
        rule_product = self.putawayRuleObj.create(
            {
                "company_id": location1.company_id.id,
                "product_tmpl_id": self.template.id,
                "location_in_id": location1.id,
                "location_out_id": location1.id,
            }
        )
        self.assertEqual(rule_product.location_in_id, location1)
        self.assertEqual(rule_product.product_tmpl_id, self.template)
        self.assertEqual(rule_product.product_id.id, False)
        # Create rules related to variants and diferente locations
        variant1 = self.template.product_variant_ids[0]
        variant2 = self.template.product_variant_ids[1]
        variant3 = self.template.product_variant_ids[2]
        self._stock_putaway_rule_product(location1, variant1)
        self._stock_putaway_rule_product(location2, variant2)
        # Create rule according to category
        rule_category = self.putawayRuleObj.create(
            {
                "company_id": location1.company_id.id,
                "category_id": self.template.categ_id.id,
                "location_in_id": location1.id,
                "location_out_id": location1.id,
            }
        )
        self.assertEqual(rule_category.category_id, self.template.categ_id)
        self.assertEqual(rule_category.location_in_id, location1)
        self.assertEqual(rule_category.product_tmpl_id.id, False)
        self.assertEqual(rule_category.product_id.id, False)
        # Check rules related
        self.assertEqual(len(self._get_product_rules(self.template)), 4)
        self.assertEqual(len(self._get_product_rules(variant1)), 2)
        self.assertEqual(len(self._get_product_rules(variant2)), 2)
        self.assertEqual(len(self._get_product_rules(variant3)), 1)
        # Check _get_putaway_strategy
        locations = location + location.child_ids
        self.assertEqual(locations._get_putaway_strategy(variant1), location1)
        self.assertEqual(locations._get_putaway_strategy(variant2), location2)
        self.assertEqual(locations._get_putaway_strategy(variant3), location1)
