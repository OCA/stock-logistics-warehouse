# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import common


class TestTemplateFreeQty(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.template_with_variant = cls.env.ref(
            "product.product_product_11_product_template"
        )
        cls.template_with_no_variant = cls.env.ref(
            "product.product_product_10_product_template"
        )

    def test_template_free_qty(self):
        # template has 2 variants with 26 and 30 free qty, template should have 56
        self.assertEqual(self.template_with_variant.free_qty, 56)
        self.assertEqual(
            self.template_with_no_variant.free_qty,
            self.template_with_no_variant.product_variant_ids.free_qty,
        )

    def test_search_template_free_qty(self):
        template_with_free_qty_ids = (
            self.env["product.template"].search([("free_qty", ">", 0)]).ids
        )
        self.assertIn(self.template_with_variant.id, template_with_free_qty_ids)
        self.assertIn(self.template_with_no_variant.id, template_with_free_qty_ids)
        template_with_no_free_qty = self.env.ref(
            "product.product_product_22_product_template"
        )
        self.assertNotIn(template_with_no_free_qty.id, template_with_free_qty_ids)
