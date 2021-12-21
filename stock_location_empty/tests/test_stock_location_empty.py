from odoo.tests import SavepointCase


class TestStockLocationChildren(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_input = cls.env["stock.location"].create(
            {
                "name": "Test",
                "usage": "internal",
            }
        )
        cls.stock_quant1 = cls.env["stock.quant"].create(
            {
                "product_id": cls.env.ref("product.product_delivery_01").id,
                "location_id": cls.stock_input.id,
                "quantity": 60,
            }
        )
        cls.stock_quant1 = cls.env["stock.quant"].create(
            {
                "product_id": cls.env.ref("product.product_delivery_02").id,
                "location_id": cls.stock_input.id,
                "quantity": 50,
            }
        )

    def test_stock_location_amount(self):
        self.assertEqual(self.stock_input.stock_amount, 110.0)
        location_record = self.env["stock.location"].search(
            [("stock_amount", "=", 110.0)]
        )
        self.assertEqual(location_record.stock_amount, 110)
        record_search = self.env["stock.location"].search(
            [("stock_amount", "in", [110, 111])]
        )
        all_record = self.env["stock.location"].search([])
        self.assertEqual(record_search, all_record)
