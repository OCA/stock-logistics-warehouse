from odoo.tests import common


class TestSaleStockOnHandPopup(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Product = cls.env["product.product"]

        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_2 = cls.env.ref("product.product_product_2")

    def test_action_open_quants_show_products(self):
        action_data = self.product_1.action_open_quants_show_products()

        self.assertNotEqual(
            action_data,
            self.product_1.action_open_quants(),
        )
        self.assertEqual("Stock Lines", action_data.get("name"))

        context = action_data.get("context")
        self.assertFalse(context.get("single_product", True))
        self.assertFalse(context.get("edit", True))
