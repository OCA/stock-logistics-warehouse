# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase


class TestStockPickingCompletionInfo(SavepointCase):
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
        cls.pick_type.write({"display_completion_info": True})

        cls.product_1 = cls.env["product.product"].create(
            {"name": "Product 1", "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Product 2", "type": "product"}
        )

    def _init_inventory(self, same_location=True):
        # Product 1 on shelf 1
        # Product 2 on shelf 2
        inventory = self.env["stock.inventory"].create({"name": "Test init"})
        inventory.action_start()
        if not same_location:
            product_location_list = [
                (self.product_1, self.stock_shelf_location),
                (self.product_2, self.stock_shelf_2_location),
            ]
        else:
            product_location_list = [
                (self.product_1, self.stock_shelf_location),
                (self.product_2, self.stock_shelf_location),
            ]
        lines_vals = list()
        for product, location in product_location_list:
            lines_vals.append(
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "product_uom_id": product.uom_id.id,
                        "product_qty": 10.0,
                        "location_id": location.id,
                    },
                )
            )
        inventory.write({"line_ids": lines_vals})
        inventory.action_validate()

    def _create_pickings(self, same_pick_location=True):
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
        if same_pick_location:
            return ship_order, pack_order, pick_order
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
        }
        if move_dest:
            move_vals["move_dest_ids"] = [(4, move_dest.id, False)]
        return self.env["stock.move"].create(move_vals)

    def test_picking_all_at_once(self):
        self._init_inventory()
        ship_order, pack_order, pick_order = self._create_pickings()
        ship_move_1 = self._create_move(ship_order, self.product_1)
        pack_move_1 = self._create_move(
            pack_order, self.product_1, move_dest=ship_move_1
        )
        pick_move_1 = self._create_move(
            pick_order,
            self.product_1,
            state="confirmed",
            procure_method="make_to_stock",
            move_dest=pack_move_1,
        )
        ship_move_2 = self._create_move(ship_order, self.product_2)
        pack_move_2 = self._create_move(
            pack_order, self.product_2, move_dest=ship_move_2
        )
        pick_move_2 = self._create_move(
            pick_order,
            self.product_2,
            state="confirmed",
            procure_method="make_to_stock",
            move_dest=pack_move_2,
        )
        self.assertEqual(pick_move_1.state, "confirmed")
        self.assertEqual(pick_move_2.state, "confirmed")
        self.assertEqual(pick_order.state, "confirmed")
        self.assertEqual(pick_order.completion_info, "full_order_picking")
        pick_order.action_assign()
        self.assertEqual(pick_move_1.state, "assigned")
        self.assertEqual(pick_move_2.state, "assigned")
        self.assertEqual(pick_order.state, "assigned")
        self.assertEqual(pick_order.completion_info, "full_order_picking")
        wiz = self.env["stock.immediate.transfer"].create(
            {"pick_ids": [(4, pick_order.id)]}
        )
        wiz.process()
        self.assertEqual(pick_move_1.state, "done")
        self.assertEqual(pick_move_2.state, "done")
        self.assertEqual(pick_order.state, "done")
        self.assertEqual(pick_order.completion_info, "next_picking_ready")

    def test_picking_from_different_locations(self):
        self._init_inventory(same_location=False)
        ship_order, pack_order, pick_order_1, pick_order_2 = self._create_pickings(
            same_pick_location=False
        )
        ship_move_1 = self._create_move(ship_order, self.product_1)
        pack_move_1 = self._create_move(
            pack_order, self.product_1, move_dest=ship_move_1
        )
        pick_move_1 = self._create_move(
            pick_order_1,
            self.product_1,
            state="confirmed",
            procure_method="make_to_stock",
            move_dest=pack_move_1,
        )
        ship_move_2 = self._create_move(ship_order, self.product_2)
        pack_move_2 = self._create_move(
            pack_order, self.product_2, move_dest=ship_move_2
        )
        pick_move_2 = self._create_move(
            pick_order_2,
            self.product_2,
            state="confirmed",
            procure_method="make_to_stock",
            move_dest=pack_move_2,
        )
        self.assertEqual(pick_move_1.state, "confirmed")
        self.assertEqual(pick_move_2.state, "confirmed")
        self.assertEqual(pick_order_1.state, "confirmed")
        self.assertEqual(pick_order_1.completion_info, "no")
        self.assertEqual(pick_order_2.state, "confirmed")
        self.assertEqual(pick_order_2.completion_info, "no")
        pick_order_1.action_assign()
        self.assertEqual(pick_move_1.state, "assigned")
        self.assertEqual(pick_order_1.state, "assigned")
        self.assertEqual(pick_order_1.completion_info, "no")
        pick_order_2.action_assign()
        self.assertEqual(pick_move_2.state, "assigned")
        self.assertEqual(pick_order_2.state, "assigned")
        self.assertEqual(pick_order_2.completion_info, "no")
        wiz = self.env["stock.immediate.transfer"].create(
            {"pick_ids": [(4, pick_order_1.id)]}
        )
        wiz.process()
        self.assertEqual(pick_move_1.state, "done")
        self.assertEqual(pick_order_1.state, "done")
        self.assertEqual(pick_order_1.completion_info, "no")
        self.assertNotEqual(pick_move_2.state, "done")
        self.assertNotEqual(pick_order_2.state, "done")
        self.assertEqual(pick_order_2.completion_info, "last_picking")
        wiz = self.env["stock.immediate.transfer"].create(
            {"pick_ids": [(4, pick_order_2.id)]}
        )
        wiz.process()
        self.assertEqual(pick_move_2.state, "done")
        self.assertEqual(pick_order_2.state, "done")
        self.assertEqual(pick_order_2.completion_info, "next_picking_ready")
        self.assertEqual(pick_order_1.completion_info, "next_picking_ready")

    def test_picking_with_backorder(self):
        self._init_inventory()
        ship_order, pack_order, pick_order = self._create_pickings()
        ship_move_1 = self._create_move(ship_order, self.product_1)
        pack_move_1 = self._create_move(
            pack_order, self.product_1, move_dest=ship_move_1
        )
        pick_move_1 = self._create_move(
            pick_order,
            self.product_1,
            state="confirmed",
            procure_method="make_to_stock",
            move_dest=pack_move_1,
        )
        ship_move_2 = self._create_move(ship_order, self.product_2)
        pack_move_2 = self._create_move(
            pack_order, self.product_2, move_dest=ship_move_2
        )
        pick_move_2 = self._create_move(
            pick_order,
            self.product_2,
            state="confirmed",
            procure_method="make_to_stock",
            move_dest=pack_move_2,
        )
        self.assertEqual(pick_move_1.state, "confirmed")
        self.assertEqual(pick_move_2.state, "confirmed")
        self.assertEqual(pick_order.state, "confirmed")
        self.assertEqual(pick_order.completion_info, "full_order_picking")
        pick_order.action_assign()
        self.assertEqual(pick_move_1.state, "assigned")
        self.assertEqual(pick_move_2.state, "assigned")
        self.assertEqual(pick_order.state, "assigned")
        self.assertEqual(pick_order.completion_info, "full_order_picking")
        # Process partially to create backorder
        pick_move_1.move_line_ids.qty_done = 1.0
        pick_move_2.move_line_ids.qty_done = pick_move_2.move_line_ids.product_uom_qty
        pick_order.action_done()
        pick_backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", pick_order.id)]
        )
        pick_backorder_move = pick_backorder.move_lines
        self.assertEqual(pick_move_1.state, "done")
        self.assertEqual(pick_move_2.state, "done")
        self.assertEqual(pick_order.state, "done")
        self.assertEqual(pick_backorder_move.state, "assigned")
        self.assertEqual(pick_backorder.state, "assigned")
        self.assertEqual(pick_order.completion_info, "no")
        self.assertEqual(pick_backorder.completion_info, "last_picking")
        # Process backorder
        pick_backorder_move.move_line_ids.qty_done = (
            pick_backorder_move.move_line_ids.product_uom_qty
        )
        pick_backorder.action_done()
        self.assertEqual(pick_backorder_move.state, "done")
        self.assertEqual(pick_backorder.state, "done")
        self.assertEqual(pick_order.completion_info, "next_picking_ready")
        self.assertEqual(pick_backorder.completion_info, "next_picking_ready")
