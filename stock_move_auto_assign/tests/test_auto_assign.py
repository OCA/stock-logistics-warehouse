# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import SavepointCase

from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.tests.common import mock_with_delay


class TestStockMoveAutoAssign(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.wh = cls.env.ref("stock.warehouse0")
        cls.out_type = cls.wh.out_type_id
        cls.in_type = cls.wh.in_type_id
        cls.int_type = cls.wh.int_type_id

        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.supplier_loc = cls.env.ref("stock.stock_location_suppliers")
        cls.shelf1_loc = cls.env.ref("stock.stock_location_components")
        cls.shelf2_loc = cls.env.ref("stock.stock_location_14")

        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )

    def _create_move(
        self,
        product,
        picking_type,
        qty=1.0,
        state="confirmed",
        procure_method="make_to_stock",
        move_dest=None,
    ):
        source = picking_type.default_location_src_id or self.supplier_loc
        dest = picking_type.default_location_dest_id or self.customer_loc
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

    def _update_qty_in_location(self, location, product, quantity):
        self.env["stock.quant"]._update_available_quantity(product, location, quantity)

    def test_job_assign_confirmed_move(self):
        """Test job method, assign moves matching product and location"""
        move1 = self._create_move(self.product, self.out_type)
        move2 = self._create_move(self.product, self.out_type)
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
