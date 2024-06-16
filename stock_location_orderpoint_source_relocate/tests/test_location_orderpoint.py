# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form

from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.tests.common import trap_jobs
from odoo.addons.stock_location_orderpoint.tests.common import (
    TestLocationOrderpointCommon,
)
from odoo.addons.stock_move_source_relocate.tests.common import SourceRelocateCommon


class TestLocationOrderpoint(TestLocationOrderpointCommon, SourceRelocateCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        name = "Internal Replenishment"
        cls.replenishment_location = cls.env["stock.location"].create(
            {
                "name": name,
                "location_id": cls.wh.lot_stock_id.location_id.id,
            }
        )
        cls.internal_location = cls.env["stock.location"].create(
            {
                "name": name,
                "location_id": cls.wh.lot_stock_id.id,
            }
        )
        picking_type = cls._create_picking_type(
            name, cls.replenishment_location, cls.internal_location, cls.wh
        )
        route = cls._create_route(
            name,
            picking_type,
            cls.replenishment_location,
            cls.internal_location,
            cls.wh,
        )
        cls.orderpoint = Form(cls.env["stock.location.orderpoint"])
        cls.orderpoint.location_id = cls.internal_location
        cls.orderpoint.route_id = route
        cls.orderpoint = cls.orderpoint.save()

        cls._create_incoming_move(10, cls.replenishment_location)
        cls.job_func = cls.env["stock.location.orderpoint"].run_auto_replenishment

    def test_auto_replenishment_without_relocation(self):
        with trap_jobs() as trap:
            move = self._create_outgoing_move(
                10,
                self.internal_location,
                defaults={"picking_type_id": self.wh.out_type_id.id},
            )
            self.assertEqual(move.location_id, self.internal_location)
            trap.assert_jobs_count(1, only=self.job_func)
            trap.assert_enqueued_job(
                self.job_func,
                args=(move.product_id, self.internal_location, "location_id"),
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )

            self.product.invalidate_cache()
            trap.perform_enqueued_jobs()
            replenish_move = self._get_replenishment_move(self.orderpoint)
            self._check_replenishment_move(replenish_move, 10, self.orderpoint)

    def test_auto_replenishment_with_relocation(self):
        self._create_relocate_rule(
            self.wh.lot_stock_id, self.internal_location, self.wh.out_type_id
        )
        with trap_jobs() as trap:
            move = self._create_outgoing_move(
                10,
                self.wh.lot_stock_id,
                defaults={"picking_type_id": self.wh.out_type_id.id},
            )
            self.assertEqual(move.location_id, self.internal_location)
            trap.assert_jobs_count(1, only=self.job_func)
            trap.assert_enqueued_job(
                self.job_func,
                args=(move.product_id, self.internal_location, "location_id"),
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )

            self.product.invalidate_cache()
            trap.perform_enqueued_jobs()
            replenish_move = self._get_replenishment_move(self.orderpoint)
            self._check_replenishment_move(replenish_move, 10, self.orderpoint)

    def test_auto_replenishment_with_partial_relocation(self):
        self._create_relocate_rule(
            self.wh.lot_stock_id, self.internal_location, self.wh.out_type_id
        )
        self._create_quants(self.product, self.internal_location, 1)
        with trap_jobs() as trap:
            move = self._create_outgoing_move(
                10,
                self.wh.lot_stock_id,
                defaults={"picking_type_id": self.wh.out_type_id.id},
            )
            self.assertEqual(move.location_id, self.wh.lot_stock_id)
            trap.assert_jobs_count(1, only=self.job_func)
            trap.assert_enqueued_job(
                self.job_func,
                args=(move.product_id, self.internal_location, "location_id"),
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )

            self.product.invalidate_cache()
            trap.perform_enqueued_jobs()
            replenish_move = self._get_replenishment_move(self.orderpoint)
            self._check_replenishment_move(replenish_move, 9, self.orderpoint)
