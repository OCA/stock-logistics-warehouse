# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.addons.stock_move_common_dest.tests.test_move_common_dest import (
    TestCommonMoveDest,
)


class TestMoveCommonDestSyncLocation(TestCommonMoveDest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.packing_location_1 = cls.env["stock.location"].create(
            {"name": "Packing 1", "location_id": cls.packing_location.id}
        )
        cls.packing_location_2 = cls.env["stock.location"].create(
            {"name": "Packing 2", "location_id": cls.packing_location.id}
        )
        cls.pick_handover_type = cls.warehouse.pick_type_id.copy(
            {"name": "Pick Handover", "sequence_code": "HO"}
        )
        cls.pack_post_type = cls.warehouse.pack_type_id.copy(
            {"name": "Pack Post", "sequence_code": "PPO"}
        )
        cls._update_qty_in_location(cls.stock_shelf_location, cls.product_1, 10)
        cls._update_qty_in_location(cls.stock_shelf_location, cls.product_2, 10)
        # Build chains such as we have:
        # PICK
        #  - pick_move1 -> pack_move1
        #  - pick_move2 -> pack_move2
        #  - pick_move4 -> pack_move4
        # PICK_SPECIAL
        #  - pick_move3 -> pack_move3
        # PACK
        #  - pack_move1
        #  - pack_move2
        #  - pack_move3
        # PACK_POSTE
        #  - pack_move4

        cls.pick_move1 = cls._create_single_move(cls.pick_type, cls.product_1)
        cls.pack_move1 = cls._create_single_move(
            cls.pack_type, cls.product_1, move_orig=cls.pick_move1
        )
        cls.pick_move2 = cls._create_single_move(cls.pick_type, cls.product_2)
        cls.pack_move2 = cls._create_single_move(
            cls.pack_type, cls.product_2, move_orig=cls.pick_move2
        )
        cls.pick_move3 = cls._create_single_move(cls.pick_handover_type, cls.product_1)
        cls.pack_move3 = cls._create_single_move(
            cls.pack_type, cls.product_1, move_orig=cls.pick_move3
        )
        cls.pick_move4 = cls._create_single_move(cls.pick_type, cls.product_2)
        cls.pack_move4 = cls._create_single_move(
            cls.pack_post_type, cls.product_2, move_orig=cls.pick_move4
        )
        moves = (
            cls.pick_move1
            + cls.pack_move1
            + cls.pick_move2
            + cls.pack_move2
            + cls.pick_move3
            + cls.pack_move3
            + cls.pick_move4
            + cls.pack_move4
        )
        moves._assign_picking()
        moves._action_assign()

    @classmethod
    def _update_qty_in_location(cls, location, product, quantity):
        cls.env["stock.quant"]._update_available_quantity(product, location, quantity)

    @classmethod
    def _create_single_move(cls, picking_type, product, move_orig=None):
        move_vals = {
            "name": product.name,
            "picking_type_id": picking_type.id,
            "product_id": product.id,
            "product_uom_qty": 2.0,
            "product_uom": product.uom_id.id,
            "location_id": picking_type.default_location_src_id.id,
            "location_dest_id": picking_type.default_location_dest_id.id,
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

    def test_pack_sync(self):
        self.pack_type.sync_common_move_dest_location = True
        self.pack_post_type.sync_common_move_dest_location = True
        self.pick_move1.move_line_ids.write(
            {
                "location_dest_id": self.packing_location_1.id,
                "qty_done": self.pick_move1.move_line_ids.product_uom_qty,
            }
        )
        # When we end the move pick_move1, pack_move1 becomes available
        # and we expect the moves that go in the same PACK transfer to have
        # their destination changed to be the same as move1.
        # pick_move4 should not change, because it reaches a move in a
        # different picking type,
        # pick_move3 should change because it reaches the same pack transfer.
        self.pick_move1._action_done()
        self.assertEqual(self.pick_move2.location_dest_id, self.packing_location_1)
        self.assertEqual(self.pick_move3.location_dest_id, self.packing_location_1)
        self.assertEqual(self.pick_move4.location_dest_id, self.packing_location)
        self.assertEqual(
            self.pick_move2.move_line_ids.location_dest_id, self.packing_location_1
        )
        self.assertEqual(
            self.pick_move3.move_line_ids.location_dest_id, self.packing_location_1
        )
        self.assertEqual(
            self.pick_move4.move_line_ids.location_dest_id, self.packing_location
        )

    def test_pack_no_sync(self):
        self.pack_type.sync_common_move_dest_location = False
        self.pack_post_type.sync_common_move_dest_location = False
        self.pick_move1.move_line_ids.write(
            {
                "location_dest_id": self.packing_location_1.id,
                "qty_done": self.pick_move1.move_line_ids.product_uom_qty,
            }
        )
        # No destination should change
        self.pick_move1._action_done()
        self.assertEqual(self.pick_move2.location_dest_id, self.packing_location)
        self.assertEqual(self.pick_move3.location_dest_id, self.packing_location)
        self.assertEqual(self.pick_move4.location_dest_id, self.packing_location)
        self.assertEqual(
            self.pick_move2.move_line_ids.location_dest_id, self.packing_location
        )
        self.assertEqual(
            self.pick_move3.move_line_ids.location_dest_id, self.packing_location
        )
        self.assertEqual(
            self.pick_move4.move_line_ids.location_dest_id, self.packing_location
        )

    def test_pack_post_sync(self):
        self.pack_type.sync_common_move_dest_location = True
        self.pack_post_type.sync_common_move_dest_location = True
        # When we set move4 to done, even if its dest. move has a picking
        # type with sync, it doesn't change the other moves because they are
        # not in the same picking type
        self.pick_move4.move_line_ids.write(
            {
                "location_dest_id": self.packing_location_1.id,
                "qty_done": self.pick_move1.move_line_ids.product_uom_qty,
            }
        )
        self.pick_move1._action_done()
        self.assertEqual(self.pick_move2.location_dest_id, self.packing_location)
        self.assertEqual(self.pick_move3.location_dest_id, self.packing_location)
        self.assertEqual(self.pick_move1.location_dest_id, self.packing_location)
        self.assertEqual(
            self.pick_move2.move_line_ids.location_dest_id, self.packing_location
        )
        self.assertEqual(
            self.pick_move3.move_line_ids.location_dest_id, self.packing_location
        )
        self.assertEqual(
            self.pick_move1.move_line_ids.location_dest_id, self.packing_location
        )
