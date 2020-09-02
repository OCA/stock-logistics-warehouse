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
        cls.product_a = cls.env["product.product"].create(
            {"name": "Product A", "type": "product"}
        )
        cls.product_b = cls.env["product.product"].create(
            {"name": "Product B", "type": "product"}
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
    def _create_move(cls, name, picking_type, product, quantity, move_orig=None):
        move_vals = {
            "name": name,
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
        return cls.env["stock.move"].create(move_vals)

    @classmethod
    def _create_picking(cls, moves):
        picking = cls.env["stock.picking"].create(moves._get_new_picking_values())
        moves.picking_id = picking.id
        return picking

    @classmethod
    def build_moves(cls):
        """Build a chain of moves and transfer

        That looks like:

                      PICK/001 ━►  PACK/001  ┓
                                             ┃
                      PICK/002 ┓             ┣━► OUT/001
                               ┣━► PACK/002  ┛
           INT/001 ━► PICK/003 ┛

        Each contains 2 moves, one for product and one for product2
        """
        Chain = namedtuple(
            "chain",
            "int1_a int1_b"
            # slots for the moves (product a, product b)
            " pick1_a pick1_b"
            " pick2_a pick2_b"
            " pick3_a pick3_b"
            " pack1_a pack1_b"
            " pack2_a pack2_b"
            " out1_a out1_b",
        )

        int1_a = cls._create_move("int1_a", cls.int_type, cls.product_a, 2)
        int1_b = cls._create_move("int1_b", cls.int_type, cls.product_b, 2)
        cls._create_picking(int1_a + int1_b)

        pick1_a = cls._create_move("pick1_a", cls.pick_type, cls.product_a, 2)
        pick1_b = cls._create_move("pick1_b", cls.pick_type, cls.product_b, 2)
        cls._create_picking(pick1_a + pick1_b)

        pick2_a = cls._create_move("pick2_a", cls.pick_type, cls.product_a, 2)
        pick2_b = cls._create_move("pick2_b", cls.pick_type, cls.product_b, 2)
        cls._create_picking(pick2_a + pick2_b)

        pick3_a = cls._create_move(
            "pick3_a", cls.pick_type, cls.product_a, 2, move_orig=int1_a
        )
        pick3_b = cls._create_move(
            "pick3_b", cls.pick_type, cls.product_b, 2, move_orig=int1_b
        )
        cls._create_picking(pick3_a + pick3_b)

        pack1_a = cls._create_move(
            "pack1_a", cls.pack_type, cls.product_a, 2, move_orig=pick1_a
        )
        pack1_b = cls._create_move(
            "pack1_b", cls.pack_type, cls.product_b, 2, move_orig=pick1_b
        )
        cls._create_picking(pack1_a + pack1_b)

        pack2_a = cls._create_move(
            "pack2_a", cls.pack_type, cls.product_a, 4, move_orig=pick2_a + pick3_a
        )
        pack2_b = cls._create_move(
            "pack2_b", cls.pack_type, cls.product_b, 4, move_orig=pick2_b + pick3_b
        )
        cls._create_picking(pack2_a + pack2_b)

        out1_a = cls._create_move(
            "out1_a", cls.out_type, cls.product_a, 6, move_orig=pack1_a + pack2_a
        )
        out1_b = cls._create_move(
            "out2_b", cls.out_type, cls.product_b, 6, move_orig=pack1_b + pack2_b
        )
        cls._create_picking(out1_a + out1_b)

        return Chain(
            int1_a,
            int1_b,
            pick1_a,
            pick1_b,
            pick2_a,
            pick2_b,
            pick3_a,
            pick3_b,
            pack1_a,
            pack1_b,
            pack2_a,
            pack2_b,
            out1_a,
            out1_b,
        )

    def _enable_consolidate_priority(self, picking_types):
        picking_types.consolidate_priority = True
        picking_types.flush()

    def _test_query(self, starting_move, expected):
        # we test only the result of the graph in this test, cancel/done move
        # are not filtered out, as they are filtered later
        query, params = starting_move._query_get_consolidate_moves()
        self.env.cr.execute(query, params)
        move_ids = [row[0] for row in self.env.cr.fetchall()]
        moves = self.env["stock.move"].browse(move_ids)
        self.assertEqual(
            moves,
            expected,
            "Priorities are not correct.\n\nExpected:\n{}\n\nGot:\n{}".format(
                "\n".join(
                    [
                        "* {}: {}".format(move.id, move.name)
                        for move in expected.sorted()
                    ]
                ),
                "\n".join(
                    ["* {}: {}".format(move.id, move.name) for move in moves.sorted()]
                ),
            ),
        )

    def test_query_graph_out1(self):
        # enable on OUT
        self._enable_consolidate_priority(self.chain.out1_a.picking_type_id)
        c = self.chain
        # these ones do not directly bring goods to OUT
        self._test_query(c.pick1_a, self.env["stock.move"])
        self._test_query(c.pick2_a, self.env["stock.move"])
        self._test_query(c.int1_a, self.env["stock.move"])
        self._test_query(c.pick3_a, self.env["stock.move"])
        all_before_out = (
            c.int1_a
            + c.int1_b
            + c.pick1_a
            + c.pick1_b
            + c.pick2_a
            + c.pick2_b
            + c.pick3_a
            + c.pick3_b
            + c.pack1_a
            + c.pack1_b
            + c.pack2_a
            + c.pack2_b
        )
        # these ones do directly bring goods to OUT, they consolidate the moves
        # before
        self._test_query(c.pack1_a, all_before_out)
        self._test_query(c.pack2_a, all_before_out)

    def test_query_graph_pack1(self):
        # enable on PACK
        self._enable_consolidate_priority(self.chain.pack1_a.picking_type_id)
        c = self.chain
        # this one does not directly bring goods to PACK
        self._test_query(c.int1_a, self.env["stock.move"])
        # these ones do directly bring goods to PACK, they consolidate the moves
        # before
        self._test_query(c.pick1_a, c.pick1_a + c.pick1_b)
        all_before_pack2 = (
            c.int1_a + c.int1_b + c.pick2_a + c.pick2_b + c.pick3_a + c.pick3_b
        )
        self._test_query(c.pick2_a, all_before_pack2)
        self._test_query(c.pick3_a, all_before_pack2)

    def test_query_graph_out1_pack1(self):
        # enable on OUT and PACK
        self._enable_consolidate_priority(
            self.chain.out1_a.picking_type_id | self.chain.pack1_a.picking_type_id
        )
        c = self.chain
        all_before_out = (
            c.int1_a
            + c.int1_b
            + c.pick1_a
            + c.pick1_b
            + c.pick2_a
            + c.pick2_b
            + c.pick3_a
            + c.pick3_b
            + c.pack1_a
            + c.pack1_b
            + c.pack2_a
            + c.pack2_b
        )
        self._test_query(c.pack1_a, all_before_out)
        self._test_query(c.pack2_a, all_before_out)
        self._test_query(c.pick1_a, c.pick1_a + c.pick1_b)
        all_before_pack2 = (
            c.int1_a + c.int1_b + c.pick2_a + c.pick2_b + c.pick3_a + c.pick3_b
        )
        self._test_query(c.pick2_a, all_before_pack2)

    def _move_to_done(self, move):
        self._update_qty_in_location(
            move.location_id, move.product_id, move.product_uom_qty
        )
        move.picking_id.action_assign()
        for line in move.move_line_ids:
            line.qty_done = line.product_uom_qty
        move.picking_id.action_done()
        self.assertEqual(move.state, "done")

    def all_chain_moves(self):
        return self.env["stock.move"].union(*[c for c in self.chain])

    def assert_priority(self, changed_moves, unchanged_moves):
        expected_priority = self.env["stock.move"]._consolidate_priority_value
        changed_ok = all(move.priority == expected_priority for move in changed_moves)
        unchanged_ok = all(move.priority == "1" for move in unchanged_moves)
        self.assertTrue(
            changed_ok and unchanged_ok,
            "Priorities are not correct.\n\nExpected:\n{}\n{}\n\nGot:\n{}".format(
                "\n".join(
                    [
                        "* {}: {}".format(move.name, expected_priority)
                        for move in changed_moves.sorted("id")
                    ]
                ),
                "\n".join(
                    [
                        "* {}: {}".format(move.name, "1")
                        for move in unchanged_moves.sorted("id")
                    ]
                ),
                "\n".join(
                    [
                        "* {}: {}".format(move.name, move.priority)
                        for move in self.all_chain_moves().sorted(
                            lambda m: (-int(m.priority), m.id)
                        )
                    ]
                ),
            ),
        )

    def assert_default_priority(self):
        self.assert_priority(
            # nothing is changed yet
            self.env["stock.move"],
            # all moves are unchanged
            self.all_chain_moves(),
        )

    def test_flow_pick1_done_out1_consolidate(self):
        c = self.chain
        # enable on OUT
        self._enable_consolidate_priority(c.out1_a.picking_type_id)
        self._move_to_done(self.chain.pick1_a)
        self.assert_default_priority()
        self._move_to_done(self.chain.pack1_a)
        self.assert_priority(
            c.int1_a
            + c.int1_b
            + c.pick1_b
            + c.pick2_a
            + c.pick2_b
            + c.pick3_a
            + c.pick3_b
            + c.pack1_b
            + c.pack2_a,
            # pick1 and pack2 are unchanged as already done
            c.pack1_a + c.pick1_a + c.out1_a + c.out1_b,
        )

    def test_flow_int1_done_pack_consolidate(self):
        c = self.chain
        # enable on PACK
        self._enable_consolidate_priority(c.pack2_a.picking_type_id)
        self._move_to_done(c.int1_a)
        self.assert_default_priority()
        self._move_to_done(c.pick3_a)
        self.assert_priority(
            c.int1_b + c.pick2_a + c.pick2_b + c.pick3_b,
            # int1 and pick3 are unchanged as already done
            c.int1_a + c.pick3_a
            # only moves *before* packs are changed
            + c.pack1_a + c.pack1_b + c.pack2_a + c.pack2_b
            # pick1 is unchanged because they don't
            # go to the same transfer
            + c.pick1_a + c.pick1_b
            # outgoing moves are late to the party, no impact on them
            + c.out1_a + c.out1_b,
        )
