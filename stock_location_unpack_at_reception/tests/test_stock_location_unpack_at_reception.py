# Copyright 2026 Camptocamp SA
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import RecordCapturer

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestStockLocationUnpackAtReception(BaseCommon):
    """Packages arriving in a location to unpack at reception are unpacked."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.transit_location = cls.env["stock.location"].create(
            {
                "name": "Test Transit",
                "usage": "transit",
                "location_id": cls.warehouse.view_location_id.id,
                "unpack_at_reception": True,
            }
        )
        cls.other_location = cls.env["stock.location"].create(
            {
                "name": "Test Other",
                "usage": "internal",
                "location_id": cls.warehouse.view_location_id.id,
            }
        )
        cls.product_a, cls.product_b = cls.env["product.product"].create(
            [
                {"name": "Product A", "is_storable": True},
                {"name": "Product B", "is_storable": True, "tracking": "lot"},
            ]
        )
        cls.lot_1, cls.lot_2 = cls.env["stock.lot"].create(
            [
                {"name": "LOT-1", "product_id": cls.product_b.id},
                {"name": "LOT-2", "product_id": cls.product_b.id},
            ]
        )
        for product, lot in (
            (cls.product_a, None),
            (cls.product_b, cls.lot_1),
            (cls.product_b, cls.lot_2),
        ):
            cls.env["stock.quant"]._update_available_quantity(
                product, cls.stock_location, 100, lot_id=lot
            )

    def _make_transfer(self, lines_spec, location_dest=None):
        """Reserve a transfer from stock of the given (product, quantity)."""
        location_dest = location_dest or self.transit_location
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": location_dest.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "location_id": self.stock_location.id,
                            "location_dest_id": location_dest.id,
                        }
                    )
                    for product, qty in lines_spec
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        return picking

    def _put_in_pack(self, move_lines, name, container_name=None):
        """Pack the lines in a package, optionally in a container."""
        package = move_lines._put_in_pack(package_name=name)
        if container_name:
            move_lines.action_put_in_pack(package_name=container_name)
        return package

    def _quants(self, location):
        """Return the positive quants of the test products in `location`."""
        return self.env["stock.quant"].search(
            [
                ("location_id", "=", location.id),
                ("product_id", "in", (self.product_a | self.product_b).ids),
                ("quantity", ">", 0),
            ]
        )

    def _make_chained_receipt(self, transfer):
        """Chain a receipt from the transit location to the given transfer."""
        receipt = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.transit_location.id,
                "location_dest_id": self.other_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": move.product_id.id,
                            "product_uom_qty": move.product_uom_qty,
                            "location_id": self.transit_location.id,
                            "location_dest_id": self.other_location.id,
                            "move_orig_ids": [Command.link(move.id)],
                        }
                    )
                    for move in transfer.move_ids
                ],
            }
        )
        receipt.action_confirm()
        return receipt

    def test_unpack_at_reception_default(self):
        """A location does not unpack at reception by default."""
        self.assertFalse(self.other_location.unpack_at_reception)

    def test_unpack_package(self):
        """A package arriving in a location to unpack at reception is unpacked.

        Scenario:
            1. Pack 10 A in a box, on a transfer to the transit location.
            2. Validate it.
        Expected:
            - The 10 A are in the transit location, without a package.
            - The done line still shows the box as destination package.
        """
        picking = self._make_transfer([(self.product_a, 10)])
        box = self._put_in_pack(picking.move_line_ids, "BOX-1")
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertRecordValues(
            self._quants(self.transit_location),
            [{"product_id": self.product_a.id, "quantity": 10, "package_id": False}],
        )
        self.assertEqual(picking.move_line_ids.result_package_id, box)
        self.assertFalse(box.quant_ids)

    def test_unpack_container(self):
        """A container of boxes is unpacked level by level.

        Scenario:
            1. Pack 2 lines of 5 B from the same lot in 2 boxes, both in a
               pallet, on a transfer to the transit location.
            2. Validate it.
        Expected:
            - The transfer is done.
            - Each box is unpacked once: 2 unpack moves.
            - One quant of 10 B remains in the transit location, without a
              package, and neither the boxes nor the pallet hold anything.
            - The package history keeps the pallet as container of the boxes.
        """
        picking = self._make_transfer([(self.product_b, 10)])
        move_line = picking.move_line_ids
        self.assertEqual(move_line.lot_id, self.lot_1)
        move_line.quantity = 5
        move_line.copy({"quantity": 5, "move_id": move_line.move_id.id})
        lines = picking.move_line_ids
        boxes = self._put_in_pack(lines[0], "BOX-1") | self._put_in_pack(
            lines[1], "BOX-2"
        )
        pallet = lines.action_put_in_pack(package_name="PALLET-1")
        with RecordCapturer(
            self.env["stock.move"], [("is_inventory", "=", True)]
        ) as unpack_moves:
            picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(len(unpack_moves.records), 2)
        self.assertRecordValues(
            self._quants(self.transit_location),
            [
                {
                    "product_id": self.product_b.id,
                    "lot_id": self.lot_1.id,
                    "quantity": 10,
                    "package_id": False,
                }
            ],
        )
        self.assertFalse((boxes | pallet).contained_quant_ids)
        self.assertEqual(lines.result_package_id, boxes)
        history = self.env["stock.package.history"].search(
            [("package_id", "in", boxes.ids)]
        )
        self.assertEqual(set(history.mapped("parent_dest_name")), {"PALLET-1"})

    def test_unpack_mixed_package(self):
        """A package of several products and lots is fully unpacked."""
        picking = self._make_transfer([(self.product_a, 10), (self.product_b, 200)])
        self._put_in_pack(picking.move_line_ids, "BOX-1")
        picking.button_validate()
        self.assertRecordValues(
            self._quants(self.transit_location).sorted(lambda q: q.lot_id.name or ""),
            [
                {"product_id": self.product_a.id, "lot_id": False, "quantity": 10},
                {
                    "product_id": self.product_b.id,
                    "lot_id": self.lot_1.id,
                    "quantity": 100,
                },
                {
                    "product_id": self.product_b.id,
                    "lot_id": self.lot_2.id,
                    "quantity": 100,
                },
            ],
        )
        self.assertFalse(self._quants(self.transit_location).package_id)

    def test_no_unpack_elsewhere(self):
        """A package arriving in a location not to unpack stays packed."""
        picking = self._make_transfer([(self.product_a, 10)], self.other_location)
        box = self._put_in_pack(picking.move_line_ids, "BOX-1", "PALLET-1")
        picking.button_validate()
        self.assertEqual(self._quants(self.other_location).package_id, box)
        self.assertEqual(box.parent_package_id.name, "PALLET-1")

    def test_unpack_note(self):
        """The transfer logs which packages were unpacked, and where."""
        picking = self._make_transfer([(self.product_a, 10)])
        self._put_in_pack(picking.move_line_ids, "BOX-1", "PALLET-1")
        picking.button_validate()
        self.assertIn(
            "Packages BOX-1, PALLET-1 unpacked on arrival in "
            f"{self.transit_location.display_name}.",
            picking.message_ids.mapped("body")[0],
        )

    def test_chained_partial_receipt(self):
        """A receipt chained to a packed transfer can be received partially.

        Scenario:
            1. A receipt of 50 A from the transit location is chained to a
               transfer of 50 A to it, packed in a box on a pallet.
            2. Validate the transfer.
            3. Receive 30 A on the receipt, and validate it with a backorder.
        Expected:
            - The receipt reserves the 50 A without a package.
            - The receipt is done for 30 A, and a backorder holds the 20 A left.
        """
        picking = self._make_transfer([(self.product_a, 50)])
        receipt = self._make_chained_receipt(picking)
        self.assertEqual(receipt.state, "waiting")
        self._put_in_pack(picking.move_line_ids, "BOX-1", "PALLET-1")
        picking.button_validate()
        self.assertEqual(receipt.state, "assigned")
        self.assertRecordValues(
            receipt.move_line_ids, [{"quantity": 50, "package_id": False}]
        )
        # Create the backorder without the confirmation wizard, whatever the
        # receipt type is set to.
        receipt.picking_type_id.create_backorder = "always"
        receipt.move_ids.quantity = 30
        receipt.button_validate()
        self.assertEqual(receipt.state, "done")
        self.assertEqual(receipt.move_ids.quantity, 30)
        self.assertRecordValues(
            receipt.backorder_ids.move_ids, [{"product_uom_qty": 20}]
        )

    def test_chained_receipt_package_already_there(self):
        """Packed content that arrived before the option was set stays
        reservable in its package by the chained receipt.

        Scenario:
            1. While the transit location does not unpack, a transfer of 50 A
               packed in a box is validated to it, chained to a receipt.
            2. The location is set to unpack at reception, and the receipt is
               reserved again.
        Expected:
            - The box was not unpacked, and the receipt reserves it again.
        """
        self.transit_location.unpack_at_reception = False
        picking = self._make_transfer([(self.product_a, 50)])
        receipt = self._make_chained_receipt(picking)
        box = self._put_in_pack(picking.move_line_ids, "BOX-1")
        picking.button_validate()
        self.transit_location.unpack_at_reception = True
        receipt.do_unreserve()
        receipt.action_assign()
        self.assertEqual(receipt.state, "assigned")
        self.assertRecordValues(
            receipt.move_line_ids, [{"quantity": 50, "package_id": box.id}]
        )

    def test_no_unpack_inventory(self):
        """Counting a package in a location to unpack does not unpack it."""
        box = self.env["stock.package"].create({"name": "BOX-1"})
        self.env["stock.quant"]._update_available_quantity(
            self.product_a, self.transit_location, 10, package_id=box
        )
        quant = self._quants(self.transit_location)
        quant.inventory_quantity = 12
        quant.action_apply_inventory()
        self.assertRecordValues(
            self._quants(self.transit_location),
            [{"quantity": 12, "package_id": box.id}],
        )
