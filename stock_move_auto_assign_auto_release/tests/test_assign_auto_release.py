# Copyright 2022 ACSONE SA/NV
# Copyright 2024 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.tests.common import trap_jobs
from odoo.addons.stock_available_to_promise_release.tests.common import (
    PromiseReleaseCommonCase,
)

RELEASABLE_DOMAINS = [
    [("is_auto_release_allowed", "=", True)],
    [("is_auto_release_allowed", "!=", False)],
]

NOT_RELEASABLE_DOMAINS = [
    [("is_auto_release_allowed", "=", False)],
    [("is_auto_release_allowed", "!=", True)],
]


class TestAssignAutoRelease(PromiseReleaseCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh.delivery_route_id.write(
            {
                "available_to_promise_defer_pull": True,
                "no_backorder_at_release": True,
            }
        )
        cls.in_type = cls.wh.in_type_id
        cls.loc_supplier = cls.env.ref("stock.stock_location_suppliers")
        cls.shipping = cls._out_picking(
            cls._create_picking_chain(
                cls.wh, [(cls.product1, 10)], date=datetime(2019, 9, 2, 16, 0)
            )
        )
        cls._update_qty_in_location(cls.loc_bin1, cls.product1, 5.0)
        cls.shipping.release_available_to_promise()
        cls.picking = cls._prev_picking(cls.shipping)
        cls.picking.action_assign()
        cls.unreleased_move = cls.shipping.move_lines.filtered("need_release")

    def _create_move(
        self,
        product,
        picking_type,
        qty=1.0,
        state="confirmed",
        procure_method="make_to_stock",
        move_dest=None,
    ):
        source = picking_type.default_location_src_id or self.loc_supplier
        dest = picking_type.default_location_dest_id or self.loc_customer
        move_vals = {
            "name": product.name,
            "product_id": product.id,
            "product_uom_qty": qty,
            "product_uom": product.uom_id.id,
            "picking_type_id": picking_type.id,
            "location_id": source.id,
            "location_dest_id": dest.id,
            "state": state,
            "procure_method": procure_method,
        }
        if move_dest:
            move_vals["move_dest_ids"] = [(4, move_dest.id, False)]
        return self.env["stock.move"].create(move_vals)

    def _get_job_for_method(self, jobs, method):
        for job in jobs:
            if str(job.func) == str(method):
                return job
        return None

    def _receive_product(self, product=None, qty=None):
        qty = qty or 100
        move = self._create_move(product or self.product1, self.in_type, qty=qty)
        move._action_assign()
        move.move_line_ids.qty_done = qty
        move.move_line_ids.location_dest_id = self.loc_bin1.id
        move._action_done()

    def test_product_pickings_auto_release(self):
        """Test job method, update qty available and launch auto release on
        the product"""
        self.assertEqual(1, len(self.unreleased_move))
        self.assertEqual(1, len(self.picking.move_lines))
        self.assertEqual(5, self.picking.move_lines.product_qty)
        # put stock in Stock/Shelf 1, the move has a source location in Stock
        self._update_qty_in_location(self.loc_bin1, self.product1, 100)
        with trap_jobs() as trap:
            self.product1.pickings_auto_release()
            job = self._get_job_for_method(
                trap.enqueued_jobs,
                self.unreleased_move.picking_id.auto_release_available_to_promise,
            )
            job.perform()
        self.assertFalse(self.unreleased_move.need_release)
        self.assertEqual(1, len(self.picking.move_lines))
        self.assertEqual(10, self.picking.move_lines.product_qty)

    def test_move_done_enqueue_job(self):
        """A move done enqueue 2 new jobs
        * 1 to assign other moves
        * 1 to release the other moves (This one depends on the first one)
        """
        job_func = self.product1.moves_auto_assign
        with trap_jobs() as trap:
            self._receive_product(self.product1, 100)
            # .with_delay() has been called a first one to auto assigned
            trap.assert_jobs_count(1, only=job_func)
            trap.assert_enqueued_job(
                job_func,
                args=(self.loc_bin1,),
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )
            # and a second one to auto release
            trap.assert_enqueued_job(
                self.product1.pickings_auto_release,
                args=(),
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )

            job1 = self._get_job_for_method(
                trap.enqueued_jobs, self.product1.moves_auto_assign
            )
            job2 = self._get_job_for_method(
                trap.enqueued_jobs, self.product1.pickings_auto_release
            )
            self.assertIn(job1, job2.depends_on)

    def test_picking_field_is_auto_release_allowed(self):
        self.assertFalse(self.shipping.is_auto_release_allowed)
        for domain in RELEASABLE_DOMAINS:
            self.assertFalse(self.env["stock.picking"].search(domain))
        for domain in NOT_RELEASABLE_DOMAINS:
            self.assertTrue(self.env["stock.picking"].search(domain))
        self._receive_product(self.product1, 100)
        self.product1.moves_auto_assign(self.loc_bin1)
        self.env["stock.move"].invalidate_cache()
        self.assertTrue(self.shipping.is_auto_release_allowed)
        for domain in RELEASABLE_DOMAINS:
            self.assertEqual(self.shipping, self.env["stock.picking"].search(domain))
        for domain in NOT_RELEASABLE_DOMAINS:
            self.assertNotIn(self.shipping, self.env["stock.picking"].search(domain))

    def test_move_field_is_auto_release_allowed(self):
        moves = self.shipping.move_lines
        move_released = moves.filtered(lambda m: not m.need_release)
        move_not_released = moves.filtered("need_release")
        self.assertFalse(move_released.is_auto_release_allowed)
        self.assertFalse(move_not_released.is_auto_release_allowed)
        for domain in RELEASABLE_DOMAINS:
            self.assertFalse(self.env["stock.move"].search(domain))
        for domain in NOT_RELEASABLE_DOMAINS:
            self.assertTrue(self.env["stock.move"].search(domain))
        self._receive_product(self.product1, 100)
        self.product1.moves_auto_assign(self.loc_bin1)
        self.env["stock.move"].invalidate_cache()
        self.assertFalse(move_released.is_auto_release_allowed)
        self.assertTrue(move_not_released.is_auto_release_allowed)
        for domain in RELEASABLE_DOMAINS:
            self.assertEqual(move_not_released, self.env["stock.move"].search(domain))
        for domain in NOT_RELEASABLE_DOMAINS:
            self.assertIn(move_released, self.env["stock.move"].search(domain))
            self.assertNotIn(move_not_released, self.env["stock.move"].search(domain))

    def test_picking_policy_one_async_receive(self):
        self.shipping.action_cancel()
        self.picking.action_cancel()
        shipping = self._out_picking(
            self._create_picking_chain(
                self.wh,
                [(self.product1, 10), (self.product2, 10)],
                date=datetime(2019, 9, 2, 16, 0),
            )
        )
        shipping.release_policy = "one"
        shipping.move_type = "one"
        self.assertTrue(
            all(
                move.need_release and not move.release_ready
                for move in shipping.move_lines
            )
        )
        with trap_jobs() as trap:
            self._receive_product(self.product1, 100)
            shipping.invalidate_cache()
            shipping.move_lines.invalidate_cache()
            jobs = trap.enqueued_jobs
        with trap_jobs() as trap:
            for job in jobs:
                job.perform()
            job = self._get_job_for_method(
                trap.enqueued_jobs, shipping.auto_release_available_to_promise
            )
            self.assertFalse(job)
        with trap_jobs() as trap:
            self._receive_product(self.product2, 100)
            shipping.invalidate_cache()
            shipping.move_lines.invalidate_cache()
            jobs = trap.enqueued_jobs
        with trap_jobs() as trap:
            for job in jobs:
                job.perform()
            job = self._get_job_for_method(
                trap.enqueued_jobs, shipping.auto_release_available_to_promise
            )
            job.perform()
        move_product1 = shipping.move_lines.filtered(
            lambda m: m.product_id == self.product1
        )
        move_product2 = shipping.move_lines - move_product1
        self.assertFalse(move_product2.release_ready)
        self.assertFalse(move_product2.need_release)
        self.assertFalse(move_product1.need_release)
        self.assertFalse(move_product1.release_ready)
