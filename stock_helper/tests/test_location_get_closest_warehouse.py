# Copyright 2022 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from .common import StockHelperCommonCase


class TestStockLocationGetClosestWarehouse(StockHelperCommonCase):
    def test_get_closest_warehouse(self):
        test_warehouse = self.env["stock.warehouse"].create(
            {"name": "Test Warehouse", "code": "Test WH Code"}
        )
        test_warehouse.view_location_id.location_id = self.wh.lot_stock_id.id
        location = test_warehouse.lot_stock_id

        self.assertEqual(location.get_warehouse(), self.wh)
        self.assertEqual(location.get_closest_warehouse(), test_warehouse)

        self.wh.sequence = 100
        test_warehouse.sequence = 1
        self.assertEqual(location.get_warehouse(), test_warehouse)
        self.assertEqual(location.get_closest_warehouse(), test_warehouse)

        self.wh.sequence = 1
        test_warehouse.sequence = 100
        self.assertEqual(location.get_warehouse(), self.wh)
        self.assertEqual(location.get_closest_warehouse(), test_warehouse)

    def test_get_closest_warehouse_no_warehouse(self):
        location = self.wh.lot_stock_id.create(
            {"name": "Test no warehouse", "barcode": "test_no_warehouse"}
        )
        self.assertFalse(location.get_closest_warehouse())
