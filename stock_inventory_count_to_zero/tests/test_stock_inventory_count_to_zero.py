# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.tests import TransactionCase, tagged


@freeze_time("2023-07-27", tick=True)
@tagged("-at_install", "post_install")
class TestStockInventoryCountZero(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "test inventory count to zero",
                "type": "product",
            }
        )
        StockQuant = cls.env["stock.quant"]
        cls.quant = StockQuant.create(
            {
                "product_id": cls.product_template.product_variant_ids[0].id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )

    def test_request_count_to_zero(self):
        wiz = self.env["stock.request.count"].create(
            {"quant_ids": [(6, 0, self.quant.ids)], "set_count": "zero"}
        )
        wiz.action_request_count()
        # Get quant pending to recount
        quants = self.env["stock.quant"].search(
            [
                ("inventory_quantity_set", "=", True),
                ("inventory_date", "<=", "2023-07-27"),
            ]
        )
        self.assertEqual(quants.inventory_quantity, 0.0)
        self.assertEqual(quants.inventory_diff_quantity, -10.0)
