# Copyright 2025 Camptocamp SA
# Copyright 2026  Akretion (https://www.akretion.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tests import tagged

from .common import CommonOutPull


@tagged("post_install", "-at_install")
class TestDeliverySteps(CommonOutPull):
    _test_user_groups = ("stock.group_stock_manager",)

    def test_delivery_pick_ship_with_pull_rules(self):
        """Test delivery pull rules with pick+ship configuration."""
        # Configure warehouse with pick+ship and delivery pull rules
        self.warehouse.write({"delivery_steps": "pick_ship", "delivery_pull": True})
        # Create chained delivery moves through a procurement
        moves = self._run_procurement(self.product, 10)
        # We get ship and pick moves
        self.assertEqual(len(moves), 2)
        ship_move, pick_move = moves
        self.assertEqual(ship_move.picking_type_id.code, "outgoing")
        self.assertEqual(ship_move.picking_type_id, self.warehouse.out_type_id)
        self.assertEqual(pick_move.picking_type_id.code, "internal")
        self.assertEqual(pick_move.picking_type_id, self.warehouse.pick_type_id)
        # Both are chained
        self.assertEqual(ship_move.move_orig_ids, pick_move)
        self.assertEqual(pick_move.move_dest_ids, ship_move)
        self.assertEqual(pick_move.state, "assigned")
        self.assertEqual(ship_move.state, "waiting")
        # Validating the first move makes the next one available
        self._validate_picking(pick_move.picking_id)
        self.assertEqual(pick_move.state, "done")
        self.assertEqual(ship_move.state, "assigned")
        self._validate_picking(ship_move.picking_id)
        self.assertEqual(ship_move.state, "done")

    def test_delivery_pick_pack_ship_with_pull_rules(self):
        """Test delivery pull rules with pick+pack+ship configuration."""
        # Configure warehouse with pick+ship and delivery pull rules
        self.warehouse.write(
            {"delivery_steps": "pick_pack_ship", "delivery_pull": True}
        )
        # Create chained delivery moves through a procurement
        moves = self._run_procurement(self.product, 10)
        # We get ship, pack and pick moves
        self.assertEqual(len(moves), 3)
        ship_move, pack_move, pick_move = moves
        self.assertEqual(ship_move.picking_type_id.code, "outgoing")
        self.assertEqual(ship_move.picking_type_id, self.warehouse.out_type_id)
        self.assertEqual(pack_move.picking_type_id.code, "internal")
        self.assertEqual(pack_move.picking_type_id, self.warehouse.pack_type_id)
        self.assertEqual(pick_move.picking_type_id.code, "internal")
        self.assertEqual(pick_move.picking_type_id, self.warehouse.pick_type_id)
        # All are chained
        self.assertEqual(ship_move.move_orig_ids, pack_move)
        self.assertEqual(pack_move.move_orig_ids, pick_move)
        self.assertEqual(pick_move.move_dest_ids, pack_move)
        self.assertEqual(pack_move.move_dest_ids, ship_move)
        self.assertEqual(pick_move.state, "assigned")
        self.assertEqual(pack_move.state, "waiting")
        self.assertEqual(ship_move.state, "waiting")
        # Validating the first move makes the next one available
        self._validate_picking(pick_move.picking_id)
        self.assertEqual(pick_move.state, "done")
        self.assertEqual(pack_move.state, "assigned")
        self.assertEqual(ship_move.state, "waiting")
        self._validate_picking(pack_move.picking_id)
        self.assertEqual(pack_move.state, "done")
        self.assertEqual(ship_move.state, "assigned")
        self._validate_picking(ship_move.picking_id)
        self.assertEqual(ship_move.state, "done")

    def test_delivery_multi_steps_toggle_delivery_pull(self):
        """First enable multi-steps delivery route, then enable delivery pull rules.

        Delivery route configuration should be updated accordingly.
        """
        # Configure warehouse with pick+ship at first...
        self.warehouse.delivery_steps = "pick_ship"
        # ...then enable delivery pull rules
        self.warehouse.delivery_pull = True
        # Create chained delivery moves through a procurement
        moves = self._run_procurement(self.product, 10)
        # We get ship and pick moves
        self.assertEqual(len(moves), 2)
        ship_move, pick_move = moves
        self.assertEqual(ship_move.picking_type_id.code, "outgoing")
        self.assertEqual(ship_move.picking_type_id, self.warehouse.out_type_id)
        self.assertEqual(pick_move.picking_type_id.code, "internal")
        self.assertEqual(pick_move.picking_type_id, self.warehouse.pick_type_id)
        # Both are chained
        self.assertEqual(ship_move.move_orig_ids, pick_move)
        self.assertEqual(pick_move.move_dest_ids, ship_move)
        self.assertEqual(pick_move.state, "assigned")
        self.assertEqual(ship_move.state, "waiting")
        # Validating the first move makes the next one available
        self._validate_picking(pick_move.picking_id)
        self.assertEqual(pick_move.state, "done")
        self.assertEqual(ship_move.state, "assigned")
        self._validate_picking(ship_move.picking_id)
        self.assertEqual(ship_move.state, "done")
