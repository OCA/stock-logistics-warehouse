# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from .common import DefaultPutawayCommon


class TestDefaultPutaway(DefaultPutawayCommon):
    def test_default_putaway(self):
        # This is the first warehouse strategy
        self.assertEqual(self.stock_1, self.product.default_putaway_location_id)
        self.assertEqual(
            self.stock_wh2_3,
            self.product.with_context(
                warehouse_id=self.warehouse_2
            ).default_putaway_location_id,
        )
        self.assertFalse(
            self.product_2.with_context(
                warehouse_id=self.warehouse_2
            ).default_putaway_location_id
        )
