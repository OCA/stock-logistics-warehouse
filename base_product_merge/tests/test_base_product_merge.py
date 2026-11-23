# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestBaseProductMerge(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_model = cls.env["product.product"]
        cls.product_tmpl_model = cls.env["product.template"]
        cls.base_product_merge_model = cls.env["base.product.merge"]

    def test_product_merge(self):
        # take current product count
        total_products = len(self.product_model.search([]))
        # create products
        product_1 = self.product_model.create({"name": "test product 1"})
        product_2 = self.product_model.create({"name": "test product 2"})
        product_3 = self.product_model.create({"name": "test product 3"})
        product_4 = self.product_model.create({"name": "test product 4"})

        # check product count before merge
        self.assertEqual(len(self.product_model.search([])), total_products + 4)

        # merge product_2 and product_4 with product_1
        product_merge = self.base_product_merge_model.with_context(
            active_ids=[product_1.id, product_2.id, product_4.id],
            active_model="product.product",
        ).create({})
        product_merge.dst_product_id = product_1
        product_merge.action_merge()

        # check product count before merge
        self.assertEqual(len(self.product_model.search([])), total_products + 2)
        # check product_3 exists
        self.assertTrue(product_3.exists())

    def test_product_template_merge(self):
        template_1 = self.product_tmpl_model.create({"name": "test template 1"})
        template_2 = self.product_tmpl_model.create({"name": "test template 2"})
        variant_2 = template_2.product_variant_id

        product_merge = self.base_product_merge_model.with_context(
            active_ids=[template_1.id, template_2.id],
            active_model="product.template",
        ).create({})
        product_merge.dst_product_tmpl_id = template_1
        product_merge.action_merge()

        self.assertTrue(template_1.exists())
        self.assertFalse(template_2.exists())
        self.assertFalse(variant_2.exists())

    def test_product_template_with_variants_merge(self):
        attribute = self.env["product.attribute"].create(
            {
                "name": "test attribute",
                "value_ids": [
                    Command.create({"name": "value 1"}),
                    Command.create({"name": "value 2"}),
                ],
            }
        )
        template_1 = self.product_tmpl_model.create({"name": "test template 1"})
        template_2 = self.product_tmpl_model.create(
            {
                "name": "test template 2",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [Command.set(attribute.value_ids.ids)],
                        }
                    )
                ],
            }
        )
        variants_2 = template_2.product_variant_ids

        product_merge = self.base_product_merge_model.with_context(
            active_ids=[template_1.id, template_2.id],
            active_model="product.template",
        ).create({})
        product_merge.dst_product_tmpl_id = template_1
        product_merge.action_merge()

        self.assertFalse(template_2.exists())
        self.env.invalidate_all()
        self.assertEqual(variants_2.product_tmpl_id, template_1)

    def test_product_merge_to_itself(self):
        product = self.product_model.create({"name": "test product"})
        product_merge = self.base_product_merge_model.with_context(
            active_ids=product.ids,
            active_model="product.product",
        ).create({})
        product_merge.dst_product_id = product
        with (
            self.assertRaises(UserError),
            self.assertLogs(
                "odoo.addons.base_product_merge.wizard.base_product_merge", "WARNING"
            ),
        ):
            product_merge.action_merge()

    def test_product_template_merge_to_itself(self):
        template = self.product_tmpl_model.create({"name": "test template"})
        product_merge = self.base_product_merge_model.with_context(
            active_ids=template.ids,
            active_model="product.template",
        ).create({})
        product_merge.dst_product_tmpl_id = template
        with self.assertRaises(UserError):
            product_merge.action_merge()
