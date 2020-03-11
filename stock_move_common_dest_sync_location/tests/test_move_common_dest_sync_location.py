# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.addons.stock_move_common_dest.tests.test_move_common_dest import TestCommonMoveDest


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

    def test_sync_common_move_dest_location(self):
        self.pick_type.sync_common_move_dest_location = True
        self._init_inventory()
        ship_order_1, pack_order_1, pick_order_1a, pick_order_1b = self._create_pickings()
        ship_move_1a = self._create_move(ship_order_1, self.product_1)
        pack_move_1a = self._create_move(
            pack_order_1, self.product_1, move_dest=ship_move_1a
        )
        pick_move_1a = self._create_move(
            pick_order_1a,
            self.product_1,
            state="confirmed",
            procure_method="make_to_stock",
            move_dest=pack_move_1a,
        )
        ship_move_1b = self._create_move(ship_order_1, self.product_2)
        pack_move_1b = self._create_move(
            pack_order_1, self.product_2, move_dest=ship_move_1b
        )
        pick_move_1b = self._create_move(
            pick_order_1b,
            self.product_2,
            state="confirmed",
            procure_method="make_to_stock",
            move_dest=pack_move_1b,
        )
        pick_order_1a.action_assign()
        pick_order_1b.action_assign()
        self.assertEqual(pick_move_1a.state, "assigned")
        self.assertEqual(pick_move_1b.state, "assigned")
        self.assertEqual(pick_order_1a.state, "assigned")
        self.assertEqual(pick_order_1b.state, "assigned")
        self.assertEqual(pick_move_1a.location_dest_id, self.packing_location)
        self.assertEqual(pick_move_1b.location_dest_id, self.packing_location)
        self.assertEqual(pick_order_1a.location_dest_id, self.packing_location)
        self.assertEqual(pick_order_1b.location_dest_id, self.packing_location)

        pick_move_1a.move_line_ids.write({'location_dest_id': self.packing_location_1})
        self.assertEqual(pick_move_1b.move_line_ids.location_dest_id, self.packing_location_1)
        # Test sync deactivated
        self.pick_type.sync_common_move_dest_location = False
        pick_move_1a.move_line_ids.write(
            {'location_dest_id': self.packing_location_2}
        )
        self.assertEqual(pick_move_1b.move_line_ids.location_dest_id,
                         self.packing_location_1)
