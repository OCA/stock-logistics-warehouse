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
    def test_auto_replenishment(self):
        name = "Internal Replenishment"
        replenishment_location = self.env["stock.location"].create(
            {
                "name": name,
                "location_id": self.wh.lot_stock_id.location_id.id,
            }
        )
        internal_location = replenishment_location.create(
            {
                "name": name,
                "location_id": self.wh.lot_stock_id.id,
            }
        )
        picking_type = self._create_picking_type(
            name, replenishment_location, internal_location, self.wh
        )
        route = self._create_route(
            name, picking_type, replenishment_location, internal_location, self.wh
        )

        orderpoint = Form(self.env["stock.location.orderpoint"])
        orderpoint.location_id = internal_location
        orderpoint.route_id = route
        orderpoint = orderpoint.save()

        job_func = self.env["stock.location.orderpoint"].run_auto_replenishment

        self._create_incoming_move(10, replenishment_location)
        self._create_relocate_rule(
            self.wh.lot_stock_id, internal_location, self.wh.out_type_id
        )
        with trap_jobs() as trap:
            move = self._create_outgoing_move(10, self.wh.lot_stock_id)
            move.picking_type_id = self.wh.out_type_id.id
            move._assign_picking()
            move._action_assign()
            self.assertEqual(move.location_id, internal_location)
            trap.assert_jobs_count(1, only=job_func)
            trap.assert_enqueued_job(
                orderpoint.run_auto_replenishment,
                args=(move.product_id, internal_location, "location_id"),
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )

            self.product.invalidate_cache()
            trap.perform_enqueued_jobs()
            replenish_move = self._get_replenishment_move(orderpoint)
            self._check_replenishment_move(replenish_move, 10, orderpoint)
