# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import TransactionCase


class TestCommonMoveDest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_delta = cls.env.ref("base.res_partner_4")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"delivery_steps": "pick_pack_ship"})
        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.output_location = cls.env.ref("stock.stock_location_output")
        cls.packing_location = cls.env.ref("stock.location_pack_zone")
        cls.stock_shelf_location = cls.env.ref("stock.stock_location_components")
        cls.stock_shelf_2_location = cls.env.ref("stock.stock_location_14")

        cls.out_type = cls.warehouse.out_type_id
        cls.pack_type = cls.warehouse.pack_type_id
        cls.pick_type = cls.warehouse.pick_type_id

        cls.product_1 = cls.env["product.product"].create(
            {"name": "Product 1", "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Product 2", "type": "product"}
        )

        cls.procurement_group_1 = cls.env["procurement.group"].create(
            {"name": "Test 1"}
        )

    def _init_inventory(self):
        # Product 1 on shelf 1
        # Product 2 on shelf 2
        self.env["stock.quant"]._update_available_quantity(
            self.product_1, self.stock_shelf_location, 10
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product_2, self.stock_shelf_2_location, 10
        )

    def _create_pickings(self):
        # Create delivery order
        ship_order = self.env["stock.picking"].create(
            {
                "partner_id": self.partner_delta.id,
                "location_id": self.output_location.id,
                "location_dest_id": self.customers_location.id,
                "picking_type_id": self.out_type.id,
            }
        )
        pack_order = self.env["stock.picking"].create(
            {
                "partner_id": self.partner_delta.id,
                "location_id": self.packing_location.id,
                "location_dest_id": self.output_location.id,
                "picking_type_id": self.pack_type.id,
            }
        )
        pick_order = self.env["stock.picking"].create(
            {
                "partner_id": self.partner_delta.id,
                "location_id": self.stock_shelf_location.id,
                "location_dest_id": self.packing_location.id,
                "picking_type_id": self.pick_type.id,
            }
        )
        pick_order_2 = self.env["stock.picking"].create(
            {
                "partner_id": self.partner_delta.id,
                "location_id": self.stock_shelf_2_location.id,
                "location_dest_id": self.packing_location.id,
                "picking_type_id": self.pick_type.id,
            }
        )
        return ship_order, pack_order, pick_order, pick_order_2

    def _create_move(
        self,
        picking,
        product,
        state="waiting",
        procure_method="make_to_order",
        move_dest=None,
    ):
        move_vals = {
            "name": product.name,
            "product_id": product.id,
            "product_uom_qty": 2.0,
            "product_uom": product.uom_id.id,
            "picking_id": picking.id,
            "location_id": picking.location_id.id,
            "location_dest_id": picking.location_dest_id.id,
            "state": state,
            "procure_method": procure_method,
            "group_id": self.procurement_group_1.id,
        }
        if move_dest:
            move_vals["move_dest_ids"] = [(4, move_dest.id, False)]
        return self.env["stock.move"].create(move_vals)

    def test_packing_sub_location(self):
        self._init_inventory()
        (
            ship_order_1,
            pack_order_1,
            pick_order_1a,
            pick_order_1b,
        ) = self._create_pickings()
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
        self.assertEqual(pick_move_1a.common_dest_move_ids, pick_move_1b)
        self.assertEqual(pick_move_1b.common_dest_move_ids, pick_move_1a)
        self.assertEqual(pack_move_1a.common_dest_move_ids, pack_move_1b)
        self.assertEqual(pack_move_1b.common_dest_move_ids, pack_move_1a)
        self.assertFalse(ship_move_1a.common_dest_move_ids)
        self.assertFalse(ship_move_1b.common_dest_move_ids)
        self.assertEqual(
            self.env["stock.move"].search(
                [("common_dest_move_ids", "=", pick_move_1b.id)]
            ),
            pick_move_1a,
        )
        self.assertEqual(
            self.env["stock.move"].search(
                [("common_dest_move_ids", "=", pick_move_1a.id)]
            ),
            pick_move_1b,
        )
        self.assertEqual(
            self.env["stock.move"].search(
                [("common_dest_move_ids", "in", (pick_move_1a | pick_move_1b).ids)]
            ),
            pick_move_1a | pick_move_1b,
        )
