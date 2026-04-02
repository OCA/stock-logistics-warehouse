# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon

from ..models.exception import (
    ReleaseChannelLocationPickingRestrictionError,
    ReleaseChannelLocationRestrictionError,
)


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
        # Check if destination is valid
        self.assertTrue(
            self.picking_1.move_line_ids._valid_location_release_channel_restriction(
                self.out_1
            )
        )

        self.picking_1.move_line_ids.location_dest_id = self.out_1
        self.picking_1.move_line_ids.qty_done = (
            self.picking_1.move_line_ids.reserved_qty
        )

        self.picking_1._action_done()
        self.assertEqual("done", self.picking_1.state)
        self.assertTrue(self.out_1.current_release_channel_restriction_id)

        self.assertEqual("assigned", self.delivery_1.state)

        self.picking_2 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_2.id),
            ]
        )
        # Check if destination is valid
        self.assertFalse(
            self.picking_2.move_line_ids._valid_location_release_channel_restriction(
                self.out_1
            )
        )

        # Do it anyway
        self.picking_2.move_line_ids.location_dest_id = self.out_1
        self.picking_2.move_line_ids.qty_done = (
            self.picking_2.move_line_ids.reserved_qty
        )

        with self.assertRaises(ReleaseChannelLocationPickingRestrictionError):
            self.picking_2._action_done()

    def test_release_channel_restriction_removal(self):
        """

        Assign the channel to both deliveries
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

        self.delivery_2 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.out.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_2.id),
            ]
        )
        self.delivery_2.assign_release_channel()
        self.assertEqual(self.default_channel, self.delivery_2.release_channel_id)
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
        self.assertTrue(self.out_1.current_release_channel_restriction_id)

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

        self.delivery_1.move_line_ids.qty_done = (
            self.delivery_1.move_line_ids.reserved_qty
        )
        self.delivery_1._action_done()

        # Check the release channel still restricts the out
        self.assertEqual(
            self.default_channel, self.out_1.current_release_channel_restriction_id
        )

        # Do the second delivery
        self.delivery_2.move_line_ids.qty_done = (
            self.delivery_2.move_line_ids.reserved_qty
        )
        self.delivery_2._action_done()
        self.assertFalse(self.out_1.current_release_channel_restriction_id)

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
        self.assertFalse(self.out_1.current_release_channel_restriction_id)

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

        with self.assertRaises(ReleaseChannelLocationPickingRestrictionError):
            self.picking_2._action_done()

    def test_release_channel_restriction_family_different(self):
        """
        Check that a restriction on a location in the same family
        applies with a different channel on the brother.

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

        self.channel_2 = self.env["stock.release.channel"].create(
            {
                "name": "CH 2",
            }
        )

        with self.assertRaises(ReleaseChannelLocationRestrictionError):
            self.out_2.current_release_channel_restriction_id = self.channel_2

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

        self.picking_2.move_line_ids.location_dest_id = self.out_2
        self.picking_2.move_line_ids.qty_done = (
            self.picking_2.move_line_ids.reserved_qty
        )

        with self.assertRaises(ReleaseChannelLocationPickingRestrictionError):
            self.picking_2._action_done()

    def test_remove_release_channel_restriction_family_different(self):
        """
        Check the restriction is removed after all pending moves are done.

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

        # Check the OUT 2 is also restricted
        self.assertEqual(
            self.default_channel, self.out_2.current_release_channel_restriction_id
        )

        self.delivery_2 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.out.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_2.id),
            ]
        )
        self.delivery_2.assign_release_channel()
        self.assertEqual(self.default_channel, self.delivery_2.release_channel_id)

        self.picking_2 = self.env["stock.picking"].search(
            [
                ("move_ids.location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
                ("group_id", "=", self.group_2.id),
            ]
        )

        self.picking_2.move_line_ids.location_dest_id = self.out_2
        self.picking_2.move_line_ids.qty_done = (
            self.picking_2.move_line_ids.reserved_qty
        )
        self.picking_2._action_done()

        # Deliver the first picking
        self.delivery_1.move_line_ids.qty_done = (
            self.delivery_1.move_line_ids.reserved_qty
        )
        self.delivery_1._action_done()

        self.assertEqual(
            self.default_channel, self.out_1.current_release_channel_restriction_id
        )
        self.assertEqual(
            self.default_channel, self.out_2.current_release_channel_restriction_id
        )

        self.delivery_2.move_line_ids.qty_done = (
            self.delivery_2.move_line_ids.reserved_qty
        )
        self.delivery_2._action_done()
        self.assertFalse(self.out_1.current_release_channel_restriction_id)
        self.assertFalse(self.out_2.current_release_channel_restriction_id)
