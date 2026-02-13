# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon

from ..models.exception import ReleaseChannelLocationRestrictionError


class TestReleaseChannelRestriction(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_channel = cls.env.ref(
            "stock_release_channel.stock_release_channel_default"
        )
        cls.channel_2 = cls.env["stock.release.channel"].create(
            {
                "name": "Channel 2",
            }
        )
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_ship"  # to have an output
        cls.out = cls.warehouse.wh_output_stock_loc_id

        cls.partner_1 = cls.env["res.partner"].create(
            {
                "name": "Partner 1",
            }
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "Partner 2",
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "route_ids": [Command.link(cls.warehouse.delivery_route_id.id)],
            }
        )

        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "inventory_quantity": 50.0,
            }
        )._apply_inventory()

        # Change it to view
        cls.out.usage = "view"
        cls.out.release_channel_restriction = "same"

        # Create Sub locations
        cls.out_1 = cls.env["stock.location"].create(
            {
                "name": "OUT-1",
                "location_id": cls.out.id,
            }
        )
        cls.out_2 = cls.env["stock.location"].create(
            {
                "name": "OUT-2",
                "location_id": cls.out.id,
            }
        )

        # create procurements for both partners
        cls.group_1 = cls.env["procurement.group"].create({"name": "Partner 1"})
        cls.group_2 = cls.env["procurement.group"].create({"name": "Partner 2"})
        proc_vals = {"group_id": cls.group_1, "release_channel_id": cls.default_channel}
        cls.env["procurement.group"].run(
            [
                cls.env["procurement.group"].Procurement(
                    cls.product,
                    5.0,
                    cls.product.uom_id,
                    cls.customers,
                    "Test 1",
                    "Test 1",
                    cls.env.company,
                    proc_vals,
                ),
            ]
        )

        proc_vals = {"group_id": cls.group_2, "release_channel_id": cls.default_channel}
        cls.env["procurement.group"].run(
            [
                cls.env["procurement.group"].Procurement(
                    cls.product,
                    5.0,
                    cls.product.uom_id,
                    cls.customers,
                    "Test 1",
                    "Test 1",
                    cls.env.company,
                    proc_vals,
                ),
            ]
        )

    def test_release_channel_restriction(self):
        """

        Assign the channel to the first delivery
        Transfer the linked picking
        """
        self.delivery_1 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.out.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_1.id),
            ]
        )
        self.delivery_1.assign_release_channel()
        self.assertEqual(self.default_channel, self.delivery_1.release_channel_id)
        self.picking_1 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_1.id),
            ]
        )

        self.picking_1.move_line_ids.location_dest_id = self.out_1
        self.picking_1.move_line_ids.qty_done = (
            self.picking_1.move_line_ids.reserved_qty
        )

        self.picking_1._action_done()
        self.assertEqual("done", self.picking_1.state)

        self.assertEqual("assigned", self.delivery_1.state)

        self.picking_2 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_2.id),
            ]
        )
        self.picking_2.move_line_ids.location_dest_id = self.out_1
        self.picking_2.move_line_ids.qty_done = (
            self.picking_2.move_line_ids.reserved_qty
        )

        with self.assertRaises(ReleaseChannelLocationRestrictionError):
            self.picking_2._action_done()

    def test_release_channel_no_restriction(self):
        """

        Create a
        """
        self.out.release_channel_restriction = False

        self.delivery_1 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.out.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_1.id),
            ]
        )
        self.delivery_1.assign_release_channel()
        self.assertEqual(self.default_channel, self.delivery_1.release_channel_id)
        self.picking_1 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_1.id),
            ]
        )

        self.picking_1.move_line_ids.location_dest_id = self.out_1
        self.picking_1.move_line_ids.qty_done = (
            self.picking_1.move_line_ids.reserved_qty
        )

        self.picking_1._action_done()
        self.assertEqual("done", self.picking_1.state)

        self.assertEqual("assigned", self.delivery_1.state)

        self.picking_2 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_2.id),
            ]
        )
        self.picking_2.move_line_ids.location_dest_id = self.out_1
        self.picking_2.move_line_ids.qty_done = (
            self.picking_2.move_line_ids.reserved_qty
        )

        self.picking_2._action_done()

    def test_release_channel_restriction_pending_incoming(self):
        """

        Assign the channel to the first delivery
        Transfer the linked picking
        """
        self.out_1.release_channel_restriction_in_move = True
        self.delivery_1 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.out.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_1.id),
            ]
        )
        self.delivery_1.assign_release_channel()
        self.assertEqual(self.default_channel, self.delivery_1.release_channel_id)
        self.picking_1 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_1.id),
            ]
        )
        self.picking_1.release_channel_id = self.default_channel
        self.picking_1.move_line_ids.location_dest_id = self.out_1
        self.picking_1.move_line_ids.qty_done = (
            self.picking_1.move_line_ids.reserved_qty
        )

        # Set the second delivery in the second channel
        self.delivery_2 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.out.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_2.id),
            ]
        )
        self.delivery_2.release_channel_id = self.channel_2
        self.picking_2 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_2.id),
            ]
        )
        self.picking_2.release_channel_id = self.channel_2

        with self.assertRaises(ReleaseChannelLocationRestrictionError):
            self.picking_1._action_done()

    def test_release_channel_restriction_pending_incoming_done(self):
        """
        Set both deliveries and pickings in same channel
        Transfer the first picking
        No error should be raised
        """
        self.out_1.release_channel_restriction_in_move = True
        self.delivery_1 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.out.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_1.id),
            ]
        )
        self.delivery_1.assign_release_channel()
        self.assertEqual(self.default_channel, self.delivery_1.release_channel_id)
        self.picking_1 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_1.id),
            ]
        )
        self.picking_1.release_channel_id = self.default_channel
        self.picking_1.move_line_ids.location_dest_id = self.out_1
        self.picking_1.move_line_ids.qty_done = (
            self.picking_1.move_line_ids.reserved_qty
        )

        # Set the second delivery in the second channel
        self.delivery_2 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.out.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_2.id),
            ]
        )
        self.delivery_2.release_channel_id = self.default_channel
        self.picking_2 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_2.id),
            ]
        )
        self.picking_2.release_channel_id = self.default_channel
        self.picking_1._action_done()

    def test_release_channel_restriction_children(self):
        """
        Check that a restriction on a location in the same family
        applies.

                        OUT

                OUT1            OUT2
        """
        self.delivery_1 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.out.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_1.id),
            ]
        )
        self.delivery_1.assign_release_channel()
        self.assertEqual(self.default_channel, self.delivery_1.release_channel_id)
        self.picking_1 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_1.id),
            ]
        )

        self.picking_1.move_line_ids.location_dest_id = self.out_1
        self.picking_1.move_line_ids.qty_done = (
            self.picking_1.move_line_ids.reserved_qty
        )

        self.picking_1._action_done()
        self.assertEqual("done", self.picking_1.state)

        self.assertEqual("assigned", self.delivery_1.state)

        self.picking_2 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_2.id),
            ]
        )
        # Use another sub-location
        self.picking_2.move_line_ids.location_dest_id = self.out_2
        self.picking_2.move_line_ids.qty_done = (
            self.picking_2.move_line_ids.reserved_qty
        )

        with self.assertRaises(ReleaseChannelLocationRestrictionError):
            self.picking_2._action_done()
