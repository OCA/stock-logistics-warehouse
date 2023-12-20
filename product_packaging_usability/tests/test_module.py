from odoo.tests.common import TransactionCase


class Test(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def test_action(self):
        product = self.env.ref("product.product_product_6")
        packaging = self.env["product.packaging"].create(
            {"name": "any", "product_id": product.id, "qty": 10}
        )
        action = packaging.ui_goto_packaging_view()
        self.assertIn(
            "search_default_product_id",
            action["context"],
            "Missing key 'search_default_product_id'",
        )
