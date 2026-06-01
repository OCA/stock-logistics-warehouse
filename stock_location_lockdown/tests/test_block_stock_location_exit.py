# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .common import StockLocationLockdownCommon


class TestStockLocationOutboundLockdown(StockLocationLockdownCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Internal location that holds stock, then gets blocked for outbound,
        # plus a child to assert descendant propagation.
        cls.locked_location = cls.Location.create(
            {
                "name": "outbound_locked",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.child_location = cls.Location.create(
            {
                "name": "outbound_locked_child",
                "usage": "internal",
                "location_id": cls.locked_location.id,
            }
        )
        cls.Quant._update_available_quantity(cls.product, cls.locked_location, 10)
        cls.Quant._update_available_quantity(cls.product, cls.child_location, 10)

        # block_stock_exit has no "cannot block stocked location" guard, so the
        # flag can be set after stock is already present.
        cls.locked_location.block_stock_exit = True

    def test_outbound_flag_propagates_to_child(self):
        """The outbound block aggregates down the location tree."""
        self.assertTrue(self.locked_location.is_outbound_blocked)
        self.assertTrue(self.child_location.is_outbound_blocked)
        # Outbound block must not imply inbound block.
        self.assertFalse(self.locked_location.is_inbound_blocked)

    def test_move_out_of_blocked_location(self):
        """Validating a move out of an outbound-blocked location is refused."""
        move = self._create_move(self.locked_location, self.customer_location, 5)
        with self.assertRaises(ValidationError):
            move._action_done()

    def test_move_out_of_blocked_child_location(self):
        """The block reaches descendants through is_outbound_blocked."""
        move = self._create_move(self.child_location, self.customer_location, 5)
        with self.assertRaises(ValidationError):
            move._action_done()

    def test_move_into_blocked_location_allowed(self):
        """Outbound block does not prevent putting stock into the location."""
        move = self._create_move(self.supplier_location, self.locked_location, 3)
        move._action_done()
        self.assertEqual(move.state, "done")

    def test_quant_cannot_leave_blocked_location(self):
        """Reassigning a quant out of a blocked location is refused in write."""
        quant = self.Quant.search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.locked_location.id),
            ]
        )
        with self.assertRaises(ValidationError):
            quant.write({"location_id": self.free_location.id})

    def test_quant_can_leave_once_unblocked(self):
        """Once the flag is cleared the quant can be moved again."""
        self.locked_location.block_stock_exit = False
        quant = self.Quant.search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.locked_location.id),
            ]
        )
        quant.write({"location_id": self.free_location.id})
        self.assertEqual(quant.location_id, self.free_location)
