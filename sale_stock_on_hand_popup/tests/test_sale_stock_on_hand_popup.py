from odoo.tests import common


class TestSaleStockOnHandPopup(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_1 = cls.env.ref("product.product_product_6")
        cls.product_2 = cls.env.ref("product.product_product_7")

    def test_action_open_quants_show_products(self):
        action_data = self.product_1.action_open_quants_show_products()

        self.assertEqual(self.product_1.display_name, action_data.get("name"))

        context = action_data.get("context")
        self.assertEqual(self.product_1.id, context.get("default_product_id"))

    def test_get_stock_quant(self):
        wiz_prod_1 = self.env["product.quant.wizard"].create(
            {
                "product_id": self.product_1.id,
            }
        )
        wiz_prod_2 = self.env["product.quant.wizard"].create(
            {
                "product_id": self.product_2.id,
            }
        )
        (wiz_prod_1 | wiz_prod_2)._compute_stock_quant_ids()

        self.assertNotEqual(wiz_prod_1.stock_quant_ids, wiz_prod_2.stock_quant_ids)
        self.assertNotEqual(
            wiz_prod_1.stock_quant_ids, wiz_prod_1.product_id.stock_quant_ids
        )
