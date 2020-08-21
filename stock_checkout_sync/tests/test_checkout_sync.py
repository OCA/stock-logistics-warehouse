# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase


class CheckoutSyncCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.packing_location = cls.env.ref("stock.location_pack_zone")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"delivery_steps": "pick_pack_ship"})
        cls.stock_shelf_location = cls.env.ref("stock.stock_location_components")
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Product2", "type": "product"}
        )
        cls.pick_type = cls.warehouse.pick_type_id
        cls.pack_type = cls.warehouse.pack_type_id
        cls.procurement_group_1 = cls.env["procurement.group"].create(
            {"name": "Test 1"}
        )

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

    def assert_locations(self, expected):
        for moves, location in expected.items():
            for move in moves:
                self.assertEqual(move.location_dest_id, location)
                for line in move.move_line_ids:
                    self.assertEqual(line.location_dest_id, location)
                for dest in move.move_dest_ids:
                    self.assertEqual(dest.location_id, location)


class TestMoveCommonDestSyncLocation(CheckoutSyncCommon):
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
        cls.moves = moves = (
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

        cls.picking_pack = cls.pack_move1.picking_id
        cls.picking_pack_post = cls.pack_move4.picking_id

    def test_pack_sync(self):
        self.moves._action_assign()
        self.assertEqual(self.pick_move1.state, "assigned")
        self.assertEqual(self.pick_move2.state, "assigned")
        self.assertEqual(self.pick_move3.state, "assigned")
        self.assertEqual(self.pick_move4.state, "assigned")

        self.pack_type.checkout_sync = True
        self.pack_post_type.checkout_sync = True

        self.assertTrue(self.pick_move1.picking_id.can_sync_to_checkout)
        self.assertTrue(self.pick_move2.picking_id.can_sync_to_checkout)
        self.assertTrue(self.pick_move3.picking_id.can_sync_to_checkout)
        self.assertTrue(self.pick_move4.picking_id.can_sync_to_checkout)

        wizard = self.env["stock.move.checkout.sync"]._create_self(
            self.pick_move1.picking_id
        )
        self.assertRecordValues(
            wizard,
            [
                {
                    "picking_ids": self.pick_move1.picking_id.ids,
                    "move_ids": (
                        self.pick_move1 | self.pick_move2 | self.pick_move3
                    ).ids,
                    "dest_picking_id": self.picking_pack.id,
                    "remaining_help": (
                        "<ul><li><strong>{}: 3 move(s)</strong></li>\n"
                        "<li>{}: 1 move(s)</li></ul>"
                    ).format(self.picking_pack.name, self.picking_pack_post.name),
                    "done_dest_picking_ids": [],
                    # True because we have another picking to sync after
                    "show_skip_button": True,
                }
            ],
        )
        wizard.location_id = self.packing_location_1
        next_action = wizard.sync()

        # Sync updated the destinations
        self.assert_locations(
            {
                # these 3 moves reach the same pack transfer
                self.pick_move1
                | self.pick_move2
                | self.pick_move3: self.packing_location_1,
                # pick_move4 should not change, because it reaches a move in a
                # different picking,
                self.pick_move4: self.packing_location,
            }
        )

        # a new wizard has been created for the second step
        wizard = self.env["stock.move.checkout.sync"].browse(next_action["res_id"])

        self.assertRecordValues(
            wizard,
            [
                {
                    "picking_ids": self.pick_move1.picking_id.ids,
                    "move_ids": self.pick_move4.ids,
                    "dest_picking_id": self.picking_pack_post.id,
                    "remaining_help": (
                        "<ul><li>{}: 3 move(s)</li>\n"
                        "<li><strong>{}: 1 move(s)</strong></li></ul>"
                    ).format(self.picking_pack.name, self.picking_pack_post.name),
                    "done_dest_picking_ids": self.picking_pack.ids,
                    # False because it's the last step to sync
                    "show_skip_button": False,
                }
            ],
        )
        wizard.location_id = self.packing_location_2
        next_action = wizard.sync()
        self.assert_locations(
            {
                self.pick_move1
                | self.pick_move2
                | self.pick_move3: self.packing_location_1,
                self.pick_move4: self.packing_location_2,
            }
        )

    def test_pack_no_sync(self):
        self.pack_type.checkout_sync = False
        self.pack_post_type.checkout_sync = False
        self.assertFalse(self.pick_move1.picking_id.can_sync_to_checkout)
        self.assertFalse(self.pick_move2.picking_id.can_sync_to_checkout)
        self.assertFalse(self.pick_move3.picking_id.can_sync_to_checkout)
        self.assertFalse(self.pick_move4.picking_id.can_sync_to_checkout)

    def test_pack_sync_in_2_times(self):
        # In this test, instead of having all the move lines to sync at the
        # same time, we have 1 move line that we put in a selected packing
        # location. Then, we assign the other moves, we expect the new move
        # lines to have the same destination location as the first move.
        # It works because we set the selected location on the other stock.move
        # records, so the move lines inherit the move's destination location
        self.pack_type.checkout_sync = True
        self.pack_post_type.checkout_sync = True

        self.assertTrue(self.pick_move1.picking_id.can_sync_to_checkout)
        self.assertTrue(self.pick_move2.picking_id.can_sync_to_checkout)
        self.assertTrue(self.pick_move3.picking_id.can_sync_to_checkout)
        self.assertTrue(self.pick_move4.picking_id.can_sync_to_checkout)

        self.pick_move1._action_assign()
        self.assertEqual(self.pick_move1.state, "assigned")
        self.assertEqual(self.pick_move2.state, "confirmed")
        self.assertEqual(self.pick_move3.state, "confirmed")
        self.assertEqual(self.pick_move4.state, "confirmed")

        wizard = self.env["stock.move.checkout.sync"]._create_self(
            self.pick_move1.picking_id
        )
        wizard.location_id = self.packing_location_1
        wizard.sync()

        # Sync updated the destinations on the moves, but we have no move lines
        # yet
        self.assert_locations(
            {
                # these 3 moves reach the same pack transfer
                self.pick_move1
                | self.pick_move2
                | self.pick_move3: self.packing_location_1,
                # pick_move4 should not change, because it reaches a move in a
                # different picking,
                self.pick_move4: self.packing_location,
            }
        )

        (self.pick_move2 | self.pick_move3 | self.pick_move4)._action_assign()
        self.assertEqual(self.pick_move1.state, "assigned")
        self.assertEqual(self.pick_move2.state, "assigned")
        self.assertEqual(self.pick_move3.state, "assigned")
        self.assertEqual(self.pick_move4.state, "assigned")

        # same check as before, but it will check the move lines as well
        self.assert_locations(
            {
                # these 3 moves reach the same pack transfer
                self.pick_move1
                | self.pick_move2
                | self.pick_move3: self.packing_location_1,
                # pick_move4 should not change, because it reaches a move in a
                # different picking,
                self.pick_move4: self.packing_location,
            }
        )
