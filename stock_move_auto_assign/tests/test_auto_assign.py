# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.tests.common import mock_with_delay

from .common import StockMoveAutoAssignCase


class TestStockMoveAutoAssign(StockMoveAutoAssignCase):
    def test_job_assign_confirmed_move(self):
        """Test job method, assign moves matching product and location"""
        move1 = self._create_move(self.product, self.out_type)
        move2 = self._create_move(self.product, self.out_type)
        (move1 | move2)._assign_picking()
        # put stock in Stock/Shelf 1, the move has a source location in Stock
        self._update_qty_in_location(self.shelf1_loc, self.product, 100)
        self.product.moves_auto_assign(self.shelf1_loc)
        self.assertEqual(move1.state, "assigned")
        self.assertEqual(move2.state, "assigned")

    def test_move_done_enqueue_job(self):
        """A move done enqueue a new job to assign other moves"""
        move = self._create_move(self.product, self.in_type, qty=100)
        move._action_assign()
        move.move_line_ids.qty_done = 50
        move.move_line_ids.location_dest_id = self.shelf1_loc.id
        move.move_line_ids.copy(
            default={"qty_done": 50, "location_dest_id": self.shelf2_loc.id}
        )
        with mock_with_delay() as (delayable_cls, delayable):
            move._action_done()
            # .with_delay() has been called once
            self.assertEqual(delayable_cls.call_count, 1)
            delay_args, delay_kwargs = delayable_cls.call_args
            # .with_delay() is called on self.product
            self.assertEqual(delay_args, (self.product,))
            # .with_delay() with the following options
            self.assertEqual(delay_kwargs.get("identity_key"), identity_exact)
            # check what's passed to the job method 'moves_auto_assign'
            self.assertEqual(delayable.moves_auto_assign.call_count, 1)
            delay_args, delay_kwargs = delayable.moves_auto_assign.call_args
            self.assertEqual(delay_args, (self.shelf1_loc | self.shelf2_loc,))
            self.assertDictEqual(delay_kwargs, {})

    def test_move_done_service_no_job(self):
        """Service products do not enqueue job"""
        self.product.type = "service"
        move = self._create_move(self.product, self.in_type, qty=1)
        move._action_assign()
        move.move_line_ids.qty_done = 1
        move.move_line_ids.location_dest_id = self.shelf1_loc.id
        with mock_with_delay() as (delayable_cls, delayable):
            move._action_done()
            # .with_delay() has not been called
            self.assertEqual(delayable_cls.call_count, 0)

    def test_move_done_chained_no_job(self):
        """A move chained to another does not enqueue job"""
        move_out = self._create_move(
            self.product, self.out_type, qty=1, state="waiting"
        )
        move = self._create_move(self.product, self.in_type, qty=1, move_dest=move_out)
        move._action_assign()
        move.move_line_ids.qty_done = 1
        move.move_line_ids.location_dest_id = self.shelf1_loc.id
        with mock_with_delay() as (delayable_cls, delayable):
            move._action_done()
            # .with_delay() has not been called
            self.assertEqual(delayable_cls.call_count, 0)

    def test_move_done_customer_no_job(self):
        """A move with other destination than internal does not enqueue job"""
        move = self._create_move(self.product, self.out_type, qty=1)
        self._update_qty_in_location(self.shelf1_loc, self.product, 1)
        move._action_assign()
        move.move_line_ids.qty_done = 1
        move.move_line_ids.location_dest_id = self.customer_loc
        with mock_with_delay() as (delayable_cls, delayable):
            move._action_done()
            # .with_delay() has not been called
            self.assertEqual(delayable_cls.call_count, 0)
