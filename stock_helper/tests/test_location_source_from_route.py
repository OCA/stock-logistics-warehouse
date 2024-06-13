# Copyright 2022 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from .common import StockHelperCommonCase


class TestStockLocationSoruceFromRoute(StockHelperCommonCase):
    def test_get_source_location_from_route(self):
        self.wh.delivery_steps = "pick_pack_ship"
        route = self.wh.delivery_route_id

        location = self.env.ref("stock.stock_location_customers")
        source_location = location._get_source_location_from_route(
            route, "make_to_stock"
        )
        self.assertEqual(source_location, self.wh.lot_stock_id)

        source_location = location._get_source_location_from_route(
            route, "make_to_order"
        )
        self.assertEqual(source_location, self.wh.wh_output_stock_loc_id)

        location = source_location
        source_location = location._get_source_location_from_route(
            route, "make_to_order"
        )
        self.assertEqual(source_location, self.wh.wh_pack_stock_loc_id)

        location = source_location
        source_location = location._get_source_location_from_route(
            route, "make_to_stock"
        )
        self.assertEqual(source_location, self.wh.lot_stock_id)

        location = source_location
        source_location = location._get_source_location_from_route(
            route, "make_to_stock"
        )
        self.assertEqual(source_location, self.supplier_loc)
