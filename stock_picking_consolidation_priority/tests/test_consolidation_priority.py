# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import namedtuple

from odoo.tests.common import SavepointCase


class TestConsolidationPriority(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"delivery_steps": "pick_pack_ship"})
        cls.stock_shelf_location = cls.env.ref("stock.stock_location_components")
        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )

        cls.pick_type = cls.warehouse.pick_type_id
        cls.pack_type = cls.warehouse.pack_type_id
        cls.out_type = cls.warehouse.out_type_id
        cls.int_type = cls.warehouse.int_type_id
        cls.procurement_group_1 = cls.env["procurement.group"].create(
            {"name": "Test 1"}
        )

        cls.chain = cls.build_moves()

    @classmethod
    def _update_qty_in_location(cls, location, product, quantity):
        cls.env["stock.quant"]._update_available_quantity(product, location, quantity)

    @classmethod
    def _create_move_with_picking(cls, picking_type, product, quantity, move_orig=None):
        move_vals = {
            "name": product.name,
            "picking_type_id": picking_type.id,
            "product_id": product.id,
            "product_uom_qty": 2.0,
            "product_uom": product.uom_id.id,
            "location_id": picking_type.default_location_src_id.id,
            "location_dest_id": picking_type.default_location_dest_id.id
            or cls.customers_location.id,
            "state": "confirmed",
            "procure_method": "make_to_stock",
            "group_id": cls.procurement_group_1.id,
        }
        if move_orig:
            move_vals.update(
                {
                    "procure_method": "make_to_order",
                    "state": "waiting",
                    "move_orig_ids": [(6, 0, move_orig.ids)],
                }
            )
        move = cls.env["stock.move"].create(move_vals)
        picking = cls.env["stock.picking"].create(move._get_new_picking_values())
        move.picking_id = picking.id
        return move

    @classmethod
    def build_moves(cls):
        """Build a chain of moves

        That looks like:

                      PICK/001 ━►  PACK/001  ┓
                                             ┃
                      PICK/002 ┓             ┣━► OUT/001
                               ┣━► PACK/002  ┛
           INT/001 ━► PICK/003 ┛
        """
        Chain = namedtuple("chain", "int1 pick1 pick2 pick3 pack1 pack2 out1")

        int1 = cls._create_move_with_picking(cls.int_type, cls.product, 2)

        pick1 = cls._create_move_with_picking(cls.pick_type, cls.product, 2)
        pick2 = cls._create_move_with_picking(cls.pick_type, cls.product, 2)
        pick3 = cls._create_move_with_picking(
            cls.pick_type, cls.product, 2, move_orig=int1
        )

        pack1 = cls._create_move_with_picking(
            cls.pack_type, cls.product, 2, move_orig=pick1
        )

        pack2 = cls._create_move_with_picking(
            cls.pack_type, cls.product, 4, move_orig=pick2 + pick3
        )

        out1 = cls._create_move_with_picking(
            cls.out_type, cls.product, 6, move_orig=pack1 + pack2
        )

        return Chain(int1, pick1, pick2, pick3, pack1, pack2, out1)

    def _enable_consolidate_priority(self, picking_types):
        picking_types.consolidate_priority = True
        picking_types.flush()

    def _test_query(self, starting_move, expected):
        # we test only the result of the graph in this test, cancel/done move
        # are not filtered out, as they are filtered later
        query, params = starting_move._query_get_consolidate_moves()
        self.env.cr.execute(query, params)
        move_ids = [row[0] for row in self.env.cr.fetchall()]
        self.assertEqual(set(move_ids), set(expected.ids))

    def test_query_graph_out1(self):
        self._enable_consolidate_priority(self.chain.out1.picking_type_id)
        self._test_query(
            self.chain.pick1,
            self.chain.pick1
            | self.chain.pick2
            | self.chain.int1
            | self.chain.pick3
            | self.chain.pack1
            | self.chain.pack2,
        )
        self._test_query(
            self.chain.pick2,
            self.chain.pick1
            | self.chain.pick2
            | self.chain.int1
            | self.chain.pick3
            | self.chain.pack1
            | self.chain.pack2,
        )
        self._test_query(
            self.chain.int1,
            self.chain.pick1
            | self.chain.pick2
            | self.chain.int1
            | self.chain.pick3
            | self.chain.pack1
            | self.chain.pack2,
        )

    def test_query_graph_pack1(self):
        self._enable_consolidate_priority(self.chain.pack1.picking_type_id)
        self._test_query(self.chain.pick1, self.chain.pick1)
        self._test_query(
            self.chain.pick2, self.chain.int1 | self.chain.pick2 | self.chain.pick3
        )
        self._test_query(
            self.chain.int1, self.chain.int1 | self.chain.pick2 | self.chain.pick3
        )

    def test_query_graph_out1_pack1(self):
        self._enable_consolidate_priority(
            self.chain.out1.picking_type_id | self.chain.pack1.picking_type_id
        )
        self._test_query(
            self.chain.pick1,
            self.chain.pick1
            | self.chain.pick2
            | self.chain.int1
            | self.chain.pick3
            | self.chain.pack1
            | self.chain.pack2,
        )
        self._test_query(
            self.chain.pick1,
            self.chain.pick1
            | self.chain.pick2
            | self.chain.int1
            | self.chain.pick3
            | self.chain.pack1
            | self.chain.pack2,
        )
        self._test_query(
            self.chain.int1,
            self.chain.pick1
            | self.chain.pick2
            | self.chain.int1
            | self.chain.pick3
            | self.chain.pack1
            | self.chain.pack2,
        )

    def _move_to_done(self, move):
        self._update_qty_in_location(
            move.location_id, move.product_id, move.product_uom_qty
        )
        move.picking_id.action_assign()
        for line in move.move_line_ids:
            line.qty_done = line.product_uom_qty
        move.picking_id.action_done()
        self.assertEqual(move.state, "done")

    def assert_priority(self, changed_moves, unchanged_moves):
        expected_priority = self.env["stock.move"]._consolidate_priority_value
        for move in changed_moves:
            self.assertEqual(move.priority, expected_priority)
        for move in unchanged_moves:
            self.assertEqual(move.priority, "1")

    def test_flow_pick1_done_out1_consolidate(self):
        self._enable_consolidate_priority(self.chain.out1.picking_type_id)
        self._move_to_done(self.chain.pick1)
        self.assert_priority(
            self.chain.pick2
            | self.chain.int1
            | self.chain.pick3
            | self.chain.pack1
            | self.chain.pack2,
            # pick1 is unchanged as already done
            self.chain.pick1 | self.chain.out1,
        )

    def test_flow_int1_done_out1_consolidate(self):
        self._enable_consolidate_priority(self.chain.out1.picking_type_id)
        self._move_to_done(self.chain.int1)
        self.assert_priority(
            self.chain.pick1
            | self.chain.pick2
            | self.chain.pick3
            | self.chain.pack1
            | self.chain.pack2,
            # int1 is unchanged as already done
            self.chain.int1 | self.chain.out1,
        )

    def test_flow_int1_done_pack_consolidate(self):
        self._enable_consolidate_priority(self.chain.pack2.picking_type_id)
        self._move_to_done(self.chain.int1)
        self.assert_priority(
            self.chain.pick2 | self.chain.pick3,
            self.chain.pick1 | self.chain.pack1
            # pack2 is unchanged as the priority is raised *before* it
            | self.chain.pack2
            # int1 is unchanged as already done
            | self.chain.int1 | self.chain.out1,
        )

    def test_flow_pick2_done_pack_consolidate(self):
        self._enable_consolidate_priority(self.chain.pack2.picking_type_id)
        self._move_to_done(self.chain.pick2)
        self.assert_priority(
            self.chain.int1 | self.chain.pick3,
            self.chain.pick1 | self.chain.pack1
            # pack2 is unchanged as the priority is raised *before* it
            | self.chain.pack2
            # pick2 is unchanged as already done
            | self.chain.pick2 | self.chain.out1,
        )
