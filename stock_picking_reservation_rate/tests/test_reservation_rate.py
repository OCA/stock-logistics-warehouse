# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from .common import ReservationRateCommon


class TestReservationRate(ReservationRateCommon):
    def test_reservation_rate(self):
        self._set_inventory()
        self._run_procurements()
        out_move_a = self.env["stock.move"].search(
            [
                ("location_dest_id", "=", self.customers.id),
                ("product_id", "=", self.product_a.id),
            ]
        )
        self.assertEqual(0.0, out_move_a.reservation_rate)
        pick_move_a = self.env["stock.move"].search(
            [
                ("location_dest_id", "=", self.out.id),
                ("product_id", "=", self.product_a.id),
            ]
        )
        self.assertEqual(100.0, pick_move_a.reservation_rate)
        pick_move_b = self.env["stock.move"].search(
            [
                ("location_dest_id", "=", self.out.id),
                ("product_id", "=", self.product_b.id),
            ]
        )
        self.assertEqual(50.0, pick_move_b.reservation_rate)
        pick_move_c = self.env["stock.move"].search(
            [
                ("location_dest_id", "=", self.out.id),
                ("product_id", "=", self.product_c.id),
            ]
        )
        self.assertEqual(0.0, pick_move_c.reservation_rate)
        # Do the pickings with partial quantities
        pick_move_a.move_line_ids.picked = True
        pick_move_a._action_done()

        pick_move_b.move_line_ids.picked = True
        pick_move_b._action_done()

        self.assertEqual(100.0, out_move_a.reservation_rate)
        self.assertEqual(50.0, out_move_a.picking_id.reservation_rate)

        # Ensure pickings are still correctly computed
        # But for product B there is a backorder
        # so, the original move has 100% reservation rate
        self.assertEqual(100.0, pick_move_a.reservation_rate)
        self.assertEqual(100.0, pick_move_b.reservation_rate)

        # Backorder
        self.assertEqual(0.0, pick_move_b.picking_id.backorder_ids.reservation_rate)
