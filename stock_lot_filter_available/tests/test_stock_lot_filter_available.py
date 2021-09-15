# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockLotFilterAvailable(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockProductionLot = cls.env["stock.production.lot"]
        cls.company = cls.env.ref("base.main_company")
        cls.loc = cls.env.ref("stock.stock_location_stock")
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "product", "tracking": "lot"}
        )
        cls.lot = cls.StockProductionLot.create(
            {
                "name": "TT-LOT",
                "product_id": cls.product.id,
                "company_id": cls.company.id,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.loc, 100, lot_id=cls.lot
        )

    def test_bad_operator(self):
        with self.assertRaises(ValueError):
            self.StockProductionLot._search_product_qty("in", [10, 15])

    def test_good_operator(self):
        domain = self.StockProductionLot._search_product_qty(">", 0)
        self.assertTrue(self.lot.id in domain[0][2])
        domain = self.StockProductionLot._search_product_qty(">", 2)
        self.assertTrue(self.lot.id in domain[0][2])
