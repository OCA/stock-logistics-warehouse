# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import StockLocationLockdownCommon


class TestStockLocationReservationLock(StockLocationLockdownCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loc = cls.Location.create(
            {
                "name": "resv_lock",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.Quant._update_available_quantity(cls.product, cls.loc, 10)

    def _quant(self):
        return self.Quant.search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.loc.id),
            ]
        )

    def _available(self):
        return self.Quant._get_available_quantity(self.product, self.loc, strict=True)

    def test_block_makes_stock_unavailable(self):
        self.assertEqual(self._available(), 10)
        self.loc.block_stock_exit = True
        quant = self._quant()
        self.assertTrue(quant.is_outbound_reservation_locked)
        self.assertEqual(quant.reserved_quantity, 10)
        self.assertEqual(quant.lock_real_reserved, 0)
        self.assertEqual(self._available(), 0)

    def test_unblock_restores_availability(self):
        self.loc.block_stock_exit = True
        self.loc.block_stock_exit = False
        quant = self._quant()
        self.assertFalse(quant.is_outbound_reservation_locked)
        self.assertEqual(quant.reserved_quantity, 0)
        self.assertEqual(self._available(), 10)

    def test_existing_reservation_preserved_through_block_cycle(self):
        self.Quant._update_reserved_quantity(self.product, self.loc, 6)
        self.assertEqual(self._available(), 4)

        # Block: the real reservation is parked, reserved is pinned to quantity.
        self.loc.block_stock_exit = True
        quant = self._quant()
        self.assertEqual(quant.reserved_quantity, 10)
        self.assertEqual(quant.lock_real_reserved, 6)
        self.assertEqual(self._available(), 0)

        # Unblock: the genuine 6-unit reservation comes back untouched.
        self.loc.block_stock_exit = False
        quant = self._quant()
        self.assertEqual(quant.reserved_quantity, 6)
        self.assertEqual(self._available(), 4)

    def test_unreserve_while_blocked_does_not_leak(self):
        """The scenario that broke the snapshot field: a real reservation is
        cancelled while the location is blocked. The freed stock must NOT
        become available."""
        self.Quant._update_reserved_quantity(self.product, self.loc, 6)
        self.loc.block_stock_exit = True

        # Cancel the genuine reservation while blocked.
        self.Quant._update_reserved_quantity(self.product, self.loc, -6)
        quant = self._quant()
        self.assertEqual(quant.lock_real_reserved, 0)
        self.assertEqual(quant.reserved_quantity, 10)  # still pinned
        self.assertEqual(self._available(), 0)  # not reopened

        # Unblock: nothing leaked, full stock available again.
        self.loc.block_stock_exit = False
        quant = self._quant()
        self.assertEqual(quant.reserved_quantity, 0)
        self.assertEqual(self._available(), 10)
