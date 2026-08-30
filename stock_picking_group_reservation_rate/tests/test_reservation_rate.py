# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tools.safe_eval import safe_eval

from odoo.addons.queue_job.tests.common import trap_jobs
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
        cls.warehouse.out_type_id.additional_picking_type_group_id = cls.type_group

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

    def test_reservation_rate_several_locations(self):
        """
        Test the case a product is stored in several zones
        """
        self._set_inventory()
        self.env["stock.quant"].create(
            {
                "location_id": self.location_a_1.id,
                "product_id": self.product_a.id,
                "inventory_quantity": 5.0,
            }
        )._apply_inventory()

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

        # Change the route for product A to zone B and run
        # a procurement
        self.product_a.route_ids = False
        self.product_a.route_ids = self.route_b

        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_a,
                    5.0,
                    self.product_a.uom_id,
                    self.customers,
                    "Test A bis",
                    "Test A bis",
                    self.env.company,
                    {"partner_id": self.partner.id, "group_id": self.group},
                ),
            ]
        )

        self.assertEqual(0.0, pick_move_c.reservation_rate)

        # Pick A has reservation rate of 100 %
        # Pick B has a reservation rate of 50% for a move and 0% for another move
        self.assertAlmostEqual(
            45.83, pick_move_a.picking_id.type_group_reservation_rate, places=2
        )

        self.assertEqual(0.0, out_move_a.picking_id.type_group_reservation_rate)

    def test_reservation_rate_several_locations_wizard(self):
        """
        Test the case a product is stored in several zones
        """
        self._set_inventory()
        self.env["stock.quant"].create(
            {
                "location_id": self.location_a_1.id,
                "product_id": self.product_a.id,
                "inventory_quantity": 5.0,
            }
        )._apply_inventory()

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

        # Change the route for product A to zone B and run
        # a procurement
        self.product_a.route_ids = False
        self.product_a.route_ids = self.route_b
        type_group_reservation_rate = self.env["stock.move"]._fields[
            "type_group_reservation_rate"
        ]
        type_group_reservation_rate_picking = self.env["stock.picking"]._fields[
            "type_group_reservation_rate"
        ]

        # First check to load value in cache
        self.assertAlmostEqual(
            50.0, pick_move_a.picking_id.type_group_reservation_rate, places=2
        )

        with (
            self.env.protecting([type_group_reservation_rate], pick_move_a),
            self.env.protecting(
                [type_group_reservation_rate_picking], pick_move_a.picking_id
            ),
        ):
            self.env["procurement.group"].run(
                [
                    self.env["procurement.group"].Procurement(
                        self.product_a,
                        5.0,
                        self.product_a.uom_id,
                        self.customers,
                        "Test A bis",
                        "Test A bis",
                        self.env.company,
                        {"partner_id": self.partner.id, "group_id": self.group},
                    ),
                ]
            )

            self.assertEqual(0.0, pick_move_c.reservation_rate)

            # Pick A has reservation rate of 100 %
            # Pick B has a reservation rate of 50% for a move and 0% for another move
            self.assertAlmostEqual(
                50.0, pick_move_a.picking_id.type_group_reservation_rate, places=2
            )

        self.assertEqual(0.0, out_move_a.picking_id.type_group_reservation_rate)
        group = pick_move_a.picking_id.picking_type_id.picking_type_group_id
        action = group.action_recompute_type_group_reservation_rate()
        wizard_model = action.get("res_model")
        self.assertIn(
            "recompute.stock.group.reservation.rate",
            wizard_model,
        )

        wizard = (
            self.env[wizard_model]
            .with_context(**safe_eval(action.get("context")))
            .create({})
        )

        with trap_jobs() as trapped_jobs:
            wizard.recompute()
            trapped_jobs.assert_jobs_count(1)
            trapped_jobs.perform_enqueued_jobs()

        self.assertAlmostEqual(
            45.83, pick_move_a.picking_id.type_group_reservation_rate, places=2
        )

    def test_reservation_rate_zero(self):
        """
        Test the case a move with 0 demand
        """
        self._set_inventory()
        move = self.env["stock.move"].create(
            {
                "product_id": self.product_a.id,
                "product_uom": self.product_a.uom_id.id,
                "product_uom_qty": 0.0,
                "name": "Product A",
                "location_id": self.stock.id,
                "location_dest_id": self.customers.id,
                "group_id": self.group.id,
            }
        )

        self.assertEqual(
            0.0,
            move.type_group_reservation_rate,
        )

    def test_additional_reservation_rate(self):
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
        self.assertEqual(
            50.0, out_move_a.picking_id.additional_type_group_reservation_rate
        )
