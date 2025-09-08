# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from freezegun import freeze_time

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.stock.tests.common import TestStockCommon


class StockMaturityCase(TestStockCommon, BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cabrales_cheese = cls.env["product.template"].create(
            {
                "name": "Cabrales Cheese",
                "is_storable": True,
                "tracking": "lot",
                "use_maturity_date": True,
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.lot_1 = cls.env["stock.lot"].create(
            {
                "name": "CAB0001",
                "product_id": cls.cabrales_cheese.product_variant_id.id,
                "maturity_date": "2024-12-31",
            }
        )
        cls.lot_2 = cls.lot_1.copy(
            {
                "name": "CAB0002",
                "maturity_date": "2025-01-02",
            }
        )
        cls.quant_1 = cls.env["stock.quant"].create(
            {
                "product_id": cls.cabrales_cheese.product_variant_id.id,
                "lot_id": cls.lot_1.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 5,
            }
        )
        cls.quant_2 = cls.env["stock.quant"].create(
            {
                "product_id": cls.cabrales_cheese.product_variant_id.id,
                "lot_id": cls.lot_2.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 5,
            }
        )

    def _create_maturity_move(self):
        stock_move = self._create_move(
            self.cabrales_cheese.product_variant_id,
            self.warehouse.lot_stock_id,
            self.env.ref("stock.stock_location_customers"),
            product_uom_qty=10,
        )
        stock_move._action_confirm()
        stock_move._action_assign()
        return stock_move

    @freeze_time("2025-01-01")
    def test_maturity_reservations_partially_available(self):
        stock_move = self._create_maturity_move()
        # We can only assign the quantity that's already muture
        self.assertAlmostEqual(stock_move.quantity, 5)
        # We can force the date and the we can reserve everything
        self.lot_2.maturity_date = "2025-01-01"
        stock_move._action_assign()
        self.assertAlmostEqual(stock_move.quantity, 10)

    @freeze_time("2025-01-02")
    def test_maturity_reservations_completely_available(self):
        stock_move = self._create_maturity_move()
        # For this date, all the stock is already mature
        self.assertAlmostEqual(stock_move.quantity, 10)
