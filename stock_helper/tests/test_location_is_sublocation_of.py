# Copyright 2020-2021 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from .common import StockHelperCommonCase


class TestStockLocationIsSublocationOf(StockHelperCommonCase):
    def test_is_sublocation_of_equal(self):
        self.assertTrue(self.shelf1_loc.is_sublocation_of(self.shelf1_loc))

    def test_is_sublocation_of_equal_child_ko(self):
        bin_loc = self.env["stock.location"].create(
            {"name": "bin", "location_id": self.shelf1_loc.id}
        )
        self.assertFalse(self.shelf1_loc.is_sublocation_of(bin_loc))

    def test_is_sublocation_of_equal_child_sibling(self):
        self.assertFalse(self.shelf1_loc.is_sublocation_of(self.shelf2_loc))

    def test_is_sublocation_of_any_ok(self):
        self.assertTrue(
            self.shelf1_loc.is_sublocation_of(self.stock_loc | self.customer_loc)
        )

    def test_is_sublocation_of_any_ko(self):
        self.assertFalse(
            self.shelf1_loc.is_sublocation_of(self.supplier_loc | self.customer_loc)
        )

    def test_is_sublocation_of_all_ok(self):
        self.assertTrue(
            self.shelf1_loc.is_sublocation_of(
                self.stock_loc | self.stock_loc.location_id, func=all
            )
        )

    def test_is_sublocation_of_all_ko(self):
        self.assertFalse(
            self.shelf1_loc.is_sublocation_of(
                self.stock_loc | self.customer_loc, func=all
            )
        )
        self.assertFalse(
            self.shelf1_loc.is_sublocation_of(
                self.supplier_loc | self.customer_loc, func=all
            )
        )
