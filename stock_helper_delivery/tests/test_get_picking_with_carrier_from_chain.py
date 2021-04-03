# Copyright 2021-2021 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from .common import StockHelperDeliveryCommonCase


class TestStockPickingGetCarrier(StockHelperDeliveryCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )

    def test_get_picking_with_carrier_from_pick(self):
        move1 = self._create_move(
            self.product,
            self.stock_loc,
            self.shelf1_loc,
            picking_type_id=self.wh.pick_type_id.id,
        )
        move2 = self._create_move(
            self.product,
            self.stock_loc,
            self.shelf1_loc,
            picking_type_id=self.wh.pack_type_id.id,
        )
        move3 = self._create_move(
            self.product,
            self.shelf1_loc,
            self.shelf2_loc,
            picking_type_id=self.wh.out_type_id.id,
        )
        (move1 | move2 | move3)._assign_picking()
        carrier = self.env.ref("delivery.free_delivery_carrier")
        move3.picking_id.carrier_id = carrier
        move1.move_dest_ids = move2
        move2.move_dest_ids = move3
        picking_with_carrier = move1.picking_id.get_picking_with_carrier_from_chain()
        self.assertEqual(picking_with_carrier, move3.picking_id)
        self.assertEqual(picking_with_carrier.carrier_id, carrier)

    def test_get_picking_with_carrier_from_pack(self):
        move1 = self._create_move(
            self.product,
            self.stock_loc,
            self.shelf1_loc,
            picking_type_id=self.wh.pack_type_id.id,
        )
        move2 = self._create_move(
            self.product,
            self.shelf1_loc,
            self.shelf2_loc,
            picking_type_id=self.wh.out_type_id.id,
        )
        (move1 | move2)._assign_picking()
        carrier = self.env.ref("delivery.free_delivery_carrier")
        move2.picking_id.carrier_id = carrier
        move1.move_dest_ids = move2
        picking_with_carrier = move1.picking_id.get_picking_with_carrier_from_chain()
        self.assertEqual(picking_with_carrier, move2.picking_id)
        self.assertEqual(picking_with_carrier.carrier_id, carrier)

    def test_get_picking_with_carrier_from_picking_with_existing_carrier(self):
        carrier1 = self.env.ref("delivery.free_delivery_carrier")
        carrier2 = self.env.ref("delivery.delivery_carrier")
        move1 = self._create_move(
            self.product,
            self.stock_loc,
            self.shelf1_loc,
            picking_type_id=self.wh.pack_type_id.id,
        )
        move2 = self._create_move(
            self.product,
            self.shelf1_loc,
            self.shelf2_loc,
            picking_type_id=self.wh.out_type_id.id,
        )
        (move1 | move2)._assign_picking()
        move1.picking_id.carrier_id = carrier1
        move2.picking_id.carrier_id = carrier2
        move1.move_dest_ids = move2
        picking_with_carrier = move1.picking_id.get_picking_with_carrier_from_chain()
        self.assertEqual(picking_with_carrier, move1.picking_id)
        self.assertEqual(picking_with_carrier.carrier_id, carrier1)

    def test_get_picking_with_carrier_no_picking_found(self):
        move1 = self._create_move(
            self.product,
            self.stock_loc,
            self.shelf1_loc,
            picking_type_id=self.wh.pack_type_id.id,
        )
        move2 = self._create_move(
            self.product,
            self.shelf1_loc,
            self.shelf2_loc,
            picking_type_id=self.wh.out_type_id.id,
        )
        (move1 | move2)._assign_picking()
        move1.move_dest_ids = move2
        self.assertFalse(move1.picking_id.get_picking_with_carrier_from_chain())

    def test_get_ship_from_chain(self):
        move1 = self._create_move(
            self.product,
            self.stock_loc,
            self.shelf1_loc,
            picking_type_id=self.wh.pick_type_id.id,
        )
        move2 = self._create_move(
            self.product,
            self.stock_loc,
            self.shelf1_loc,
            picking_type_id=self.wh.pack_type_id.id,
        )
        move3 = self._create_move(
            self.product,
            self.shelf1_loc,
            self.shelf2_loc,
            picking_type_id=self.wh.out_type_id.id,
        )
        (move1 | move2 | move3)._assign_picking()
        move1.move_dest_ids = move2
        move2.move_dest_ids = move3
        ship = move1.picking_id._get_ship_from_chain()
        self.assertEqual(ship, move3.picking_id)
