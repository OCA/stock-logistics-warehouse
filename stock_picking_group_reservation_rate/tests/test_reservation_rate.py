# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock_picking_reservation_rate.tests.common import (
    ReservationRateCommon,
)


class TestReservationRateGroup(ReservationRateCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.type_group = cls.env["stock.picking.type.group"].create(
            {
                "name": "Pickings",
            }
        )
        cls.type_group.picking_type_ids = (
            cls.picking_type_a | cls.picking_type_b | cls.picking_type_c
        )

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

        self.assertEqual(50.0, pick_move_a.picking_id.type_group_reservation_rate)

        self.assertEqual(0.0, out_move_a.picking_id.type_group_reservation_rate)
