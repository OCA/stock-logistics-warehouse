# Copyright 2019 Akretion France
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError

from .common import StockLocationLockdownCommon


class TestStockLocationInboundLockdown(StockLocationLockdownCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Empty internal location blocked for inbound, plus a child (to assert
        # descendant propagation) and a separately stocked location (to assert
        # the "cannot block stocked location" guard).
        cls.locked_location = cls.Location.create(
            {
                "name": "inbound_locked",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.child_location = cls.Location.create(
            {
                "name": "inbound_locked_child",
                "usage": "internal",
                "location_id": cls.locked_location.id,
            }
        )
        cls.stocked_location = cls.Location.create(
            {
                "name": "stocked",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.Quant._update_available_quantity(cls.product, cls.stocked_location, 10)
        cls.locked_location.block_stock_entrance = True

    def test_inbound_flag_propagates_to_child(self):
        """The inbound block aggregates down the location tree."""
        self.assertTrue(self.locked_location.is_inbound_blocked)
        self.assertTrue(self.child_location.is_inbound_blocked)
        # Inbound block must not imply outbound block.
        self.assertFalse(self.locked_location.is_outbound_blocked)

    def test_move_into_blocked_location(self):
        """Validating a move into an inbound-blocked location is refused."""
        move = self._create_move(self.supplier_location, self.locked_location, 5)
        with self.assertRaises(ValidationError):
            move._action_done()

    def test_move_into_blocked_child_location(self):
        """The block reaches descendants through is_inbound_blocked."""
        move = self._create_move(self.supplier_location, self.child_location, 5)
        with self.assertRaises(ValidationError):
            move._action_done()

    def test_move_out_of_blocked_location_allowed(self):
        """Inbound block does not prevent taking stock out of the location."""
        # Allow blocking a stocked location, seed stock, then block inbound.
        self.env.company.allow_lockdown_on_stocked_location = True
        out_location = self.Location.create(
            {
                "name": "inbound_locked_with_stock",
                "usage": "internal",
                "location_id": self.stock_location.id,
            }
        )
        self.Quant._update_available_quantity(self.product, out_location, 10)
        out_location.block_stock_entrance = True

        move = self._create_move(out_location, self.customer_location, 3)
        move._action_done()
        self.assertEqual(move.state, "done")

    def test_block_location_with_quants_refused(self):
        """Enabling the inbound block on a stocked location is refused."""
        with self.assertRaises(UserError):
            self.stocked_location.write({"block_stock_entrance": True})

    def test_block_stocked_location_allowed_with_company_setting(self):
        """The company setting bypasses the stocked-location guard."""
        self.env.company.allow_lockdown_on_stocked_location = True
        self.stocked_location.write({"block_stock_entrance": True})
        self.assertTrue(self.stocked_location.is_inbound_blocked)
