# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.stock_checkout_sync.tests.test_checkout_sync import CheckoutSyncCommon


class TestRoutingPullWithSync(CheckoutSyncCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location_pack_load = cls.env["stock.location"].create(
            {"name": "Packing Load", "location_id": cls.packing_location.id}
        )
        cls.location_pack_post = cls.env["stock.location"].create(
            {"name": "Packing Post", "location_id": cls.packing_location.id}
        )
        cls.location_pack_post_bay1 = cls.env["stock.location"].create(
            {"name": "Bay 1", "location_id": cls.location_pack_post.id}
        )
        cls.pack_post_type = cls.pack_type.copy(
            {
                "name": "Packing Post",
                "sequence_code": "WH/POST",
                "default_location_src_id": cls.location_pack_post.id,
            }
        )
        cls.routing = cls.env["stock.routing"].create(
            {
                "location_id": cls.location_pack_post.id,
                "picking_type_id": cls.warehouse.pack_type_id.id,
                "rule_ids": [
                    (0, 0, {"method": "pull", "picking_type_id": cls.pack_post_type.id})
                ],
            }
        )
        cls.env["stock.routing"].create(
            {
                "location_id": cls.location_pack_post.id,
                "picking_type_id": cls.pack_post_type.id,
                "rule_ids": [
                    (0, 0, {"method": "pull", "picking_type_id": cls.pack_post_type.id})
                ],
            }
        )
        cls._update_qty_in_location(cls.stock_shelf_location, cls.product_1, 10)
        cls._update_qty_in_location(cls.stock_shelf_location, cls.product_2, 10)

        cls.pick_move1 = cls._create_single_move(cls.pick_type, cls.product_1)
        cls.pack_move1 = cls._create_single_move(
            cls.pack_type, cls.product_1, move_orig=cls.pick_move1
        )
        cls.pick_move2 = cls._create_single_move(cls.pick_type, cls.product_2)
        cls.pack_move2 = cls._create_single_move(
            cls.pack_type, cls.product_2, move_orig=cls.pick_move2
        )
        cls.pick_move3 = cls._create_single_move(cls.pick_type, cls.product_2)
        cls.pack_move3 = cls._create_single_move(
            cls.pack_type, cls.product_2, move_orig=cls.pick_move3
        )
        moves = (
            cls.pick_move1
            + cls.pack_move1
            + cls.pick_move2
            + cls.pack_move2
            + cls.pick_move3
            + cls.pack_move3
        )
        moves._assign_picking()
        moves._action_assign()

    def assert_picking_type_pack(self, record):
        self.assertEqual(record.picking_type_id, self.pack_type)

    def assert_picking_type_pack_post(self, record):
        self.assertEqual(record.picking_type_id, self.pack_post_type)

    def assert_src_packing(self, record):
        self.assertEqual(record.location_id, self.packing_location)

    def assert_dest_packing(self, record):
        self.assertEqual(record.location_dest_id, self.packing_location)

    def assert_src_pack_post(self, record):
        self.assertEqual(record.location_id, self.location_pack_post)

    def assert_src_pack_post_bay1(self, record):
        self.assertEqual(record.location_id, self.location_pack_post_bay1)

    def assert_src_pack_load(self, record):
        self.assertEqual(record.location_id, self.location_pack_load)

    def assert_dest_pack_post(self, record):
        self.assertEqual(record.location_dest_id, self.location_pack_post)

    def assert_dest_pack_post_bay1(self, record):
        self.assertEqual(record.location_dest_id, self.location_pack_post_bay1)

    def assert_dest_pack_load(self, record):
        self.assertEqual(record.location_dest_id, self.location_pack_load)

    def assert_locations(self, expected):
        for moves, location in expected.items():
            for move in moves:
                self.assertEqual(move.location_dest_id, location)
                for line in move.move_line_ids:
                    self.assertEqual(line.location_dest_id, location)
                for dest in move.move_dest_ids:
                    # when the routing applies, we expect the location to be
                    # the one of the picking type
                    self.assertEqual(
                        dest.location_id, dest.picking_type_id.default_location_src_id
                    )

    def test_pack_sync(self):
        self.pack_type.checkout_sync = True
        self.pack_post_type.checkout_sync = True

        wizard = self.env["stock.move.checkout.sync"]._create_self(
            self.pick_move1.picking_id
        )
        wizard.location_id = self.location_pack_post_bay1
        wizard.sync()

        self.assert_locations(
            {
                self.pick_move1
                | self.pick_move2
                | self.pick_move3: self.location_pack_post_bay1,
            }
        )
        self.pick_move1.move_line_ids.write(
            {"qty_done": self.pick_move1.move_line_ids.product_uom_qty}
        )
        self.pick_move1._action_done()

        # check source of destination moves:
        # the routing applies the picking type's origin
        self.assert_src_pack_post(self.pack_move1)
        self.assert_src_pack_post_bay1(self.pack_move1.move_line_ids)
        # no move lines on these waiting moves:
        self.assert_src_pack_post(self.pack_move2)
        self.assert_src_pack_post(self.pack_move3)

        self.assert_picking_type_pack_post(self.pack_move1.picking_id)
        self.assert_picking_type_pack_post(self.pack_move2.picking_id)
        self.assert_picking_type_pack_post(self.pack_move3.picking_id)

    def test_pack_sync_split(self):
        self.pack_type.checkout_sync = True
        self.pack_post_type.checkout_sync = True

        self.pick_move1._do_unreserve()
        self.env["stock.quant"].search(
            [
                ("location_id", "=", self.stock_shelf_location.id),
                ("product_id", "=", self.product_1.id),
            ]
        ).unlink()

        # only 1 qty of 2 is available in Shelf
        self._update_qty_in_location(self.stock_shelf_location, self.product_1, 1)

        self.pick_move1._action_assign()

        # sync pick move 1 to have move lines set to pack post bay1
        wizard = self.env["stock.move.checkout.sync"]._create_self(
            self.pick_move1.picking_id
        )
        wizard.location_id = self.location_pack_post_bay1
        # This will update the destination, and the source location
        # of the Pack moves. Which will trigger the routing.
        wizard.sync()

        self.pick_move1.move_line_ids.write({"qty_done": 1})
        self.pick_move1._action_done()

        pick_move_split = self.pick_move1.move_dest_ids.move_orig_ids - self.pick_move1
        # the pack move should be split, one part coming from pick_move1 being
        # done, and the other part waiting for the remaining quantity.
        self.assertEqual(
            sorted(pick_move_split.move_dest_ids.mapped("state")),
            ["assigned", "waiting"],
        )
        waiting_pack = pick_move_split.move_dest_ids.filtered(
            lambda p: p.state == "waiting"
        )
        assigned_pack = pick_move_split.move_dest_ids.filtered(
            lambda p: p.state == "assigned"
        )

        self.assertEqual(pick_move_split.state, "confirmed")

        self.assert_dest_pack_post_bay1(self.pick_move1)
        self.assert_dest_pack_post_bay1(self.pick_move1.move_line_ids)
        self.assert_dest_pack_post_bay1(pick_move_split)
        self.assert_dest_pack_post_bay1(self.pick_move1)
        self.assert_dest_pack_post_bay1(self.pick_move2.move_line_ids)
        self.assert_dest_pack_post_bay1(self.pick_move3)
        self.assert_dest_pack_post_bay1(self.pick_move3.move_line_ids)

        # routing reapplies the default source location of the routing
        self.assert_src_pack_post(assigned_pack)
        self.assert_src_pack_post_bay1(assigned_pack.move_line_ids)
        # no move lines on these waiting moves:
        self.assert_src_pack_post(waiting_pack)
        self.assert_src_pack_post(self.pack_move2)
        self.assert_src_pack_post(self.pack_move3)

        self.assert_picking_type_pack_post(self.pack_move1.picking_id)
        self.assert_picking_type_pack_post(self.pack_move2.picking_id)
        self.assert_picking_type_pack_post(self.pack_move3.picking_id)
