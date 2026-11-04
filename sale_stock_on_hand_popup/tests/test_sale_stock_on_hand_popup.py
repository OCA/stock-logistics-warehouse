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

    def test_move_line_action(self):
        """
        The action of the move line shows the quants of its product.
        """
        # Arrange
        company = self.env.company
        from_location = self.env.ref("stock.stock_location_stock")
        to_location = self.env.ref("stock.stock_location_customers")
        product = self.product_1
        move_line = self.env["stock.move.line"].create(
            {
                "company_id": company.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "location_id": from_location.id,
                "location_dest_id": to_location.id,
            }
        )

        # Act
        move_line_action = move_line.action_open_quants_show_products()

        # Assert
        self.assertEqual(
            move_line_action,
            move_line.product_id.action_open_quants_show_products(),
        )

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
