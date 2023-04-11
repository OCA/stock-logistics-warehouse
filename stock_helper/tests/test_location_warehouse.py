# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from .common import StockHelperCommonCase


class TestStockLocationClosestWarehouse(StockHelperCommonCase):
    def test_closest_warehouse(self):
        test_warehouse = self.env["stock.warehouse"].create(
            {"name": "Test Warehouse", "code": "Test WH Code"}
        )
        location = test_warehouse.lot_stock_id
        location._compute_warehouse_id()
        self.assertEqual(location.warehouse_id, test_warehouse)

        test_warehouse.view_location_id.location_id = self.wh.lot_stock_id.id

        self.wh.sequence = 100
        test_warehouse.sequence = 1
        location._compute_warehouse_id()
        self.assertEqual(location.warehouse_id, test_warehouse)

        self.wh.sequence = 1
        test_warehouse.sequence = 100
        location._compute_warehouse_id()
        self.assertEqual(location.warehouse_id, test_warehouse)
