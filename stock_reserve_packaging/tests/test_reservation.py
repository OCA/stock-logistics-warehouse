# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common


class TestReservePackaging(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.loc_stock = cls.wh.lot_stock_id
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.loc1 = cls.env["stock.location"].create(
            {"name": "TestLoc1", "location_id": cls.loc_stock.id}
        )
        cls.loc2 = cls.env["stock.location"].create(
            {"name": "TestLoc2", "location_id": cls.loc_stock.id}
        )
        cls.loc3 = cls.env["stock.location"].create(
            {"name": "TestLoc3", "location_id": cls.loc_stock.id}
        )
        cls.loc4 = cls.env["stock.location"].create(
            {"name": "TestLoc4", "location_id": cls.loc_stock.id}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "Code product 1",
            }
        )

    def _setup_packagings(self, product, packagings):
        """Create packagings on a product

        packagings is a list [(name, qty)]
        """
        self.env["product.packaging"].create(
            [
                {"name": name, "qty": qty, "product_id": product.id}
                for name, qty in packagings
            ]
        )

    def _update_product_qty_in_location(
        self, location, product, quantity, reserved=0
    ):
        self.env["stock.quant"]._update_available_quantity(
            product, location, quantity
        )
        if reserved:
            self.env["stock.quant"]._update_reserved_quantity(
                product, location, reserved
            )

    def _create_picking_move(self, quantity):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.loc_stock.id,
                "location_dest_id": self.loc_customer.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "picking_id": picking.id,
                "name": "Test unit",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": quantity,
                "location_id": self.loc_stock.id,
                "location_dest_id": self.loc_customer.id,
            }
        )
        return move

    def test_full_pallet(self):
        self._setup_packagings(self.product, [("Pallet", 100)])
        self._update_product_qty_in_location(self.loc1, self.product, 80)
        self._update_product_qty_in_location(self.loc2, self.product, 100)
        move = self._create_picking_move(100)
        move.picking_id.with_context(pdb=True).action_assign()
        move_lines = move.move_line_ids
        self.assertRecordValues(
            move_lines, [{"location_id": self.loc2.id, "product_qty": 100}]
        )

    def test_no_full_pallet(self):
        self._setup_packagings(self.product, [("Pallet", 100)])
        self._update_product_qty_in_location(self.loc2, self.product, 50)
        self._update_product_qty_in_location(self.loc4, self.product, 50)
        self._update_product_qty_in_location(self.loc1, self.product, 90)
        move = self._create_picking_move(100)
        move.picking_id.action_assign()
        move_lines = move.move_line_ids
        self.assertRecordValues(
            move_lines,
            [
                {"location_id": self.loc2.id, "product_qty": 50},
                {"location_id": self.loc4.id, "product_qty": 50},
            ],
        )

    def test_box(self):
        self._setup_packagings(self.product, [("Pallet", 100), ("Box", 50)])
        self._update_product_qty_in_location(self.loc1, self.product, 20)
        self._update_product_qty_in_location(self.loc2, self.product, 30)
        self._update_product_qty_in_location(self.loc3, self.product, 50)
        self._update_product_qty_in_location(self.loc4, self.product, 50)
        move = self._create_picking_move(100)
        move.picking_id.action_assign()
        move_lines = move.move_line_ids
        self.assertRecordValues(
            move_lines,
            [
                {"location_id": self.loc3.id, "product_qty": 50},
                {"location_id": self.loc4.id, "product_qty": 50},
            ],
        )

    def test_pallet_box(self):
        self._setup_packagings(self.product, [("Pallet", 100), ("Box", 50)])
        self._update_product_qty_in_location(self.loc1, self.product, 40)
        self._update_product_qty_in_location(self.loc2, self.product, 100)
        self._update_product_qty_in_location(self.loc3, self.product, 50)
        self._update_product_qty_in_location(self.loc4, self.product, 30)
        move = self._create_picking_move(160)
        move.picking_id.action_assign()
        move_lines = move.move_line_ids
        self.assertRecordValues(
            move_lines,
            [
                {"location_id": self.loc2.id, "product_qty": 100},
                {"location_id": self.loc3.id, "product_qty": 50},
                {"location_id": self.loc1.id, "product_qty": 10},
            ],
        )

    def test_pallet_reserved(self):
        self._setup_packagings(self.product, [("Pallet", 100)])
        self._update_product_qty_in_location(
            self.loc1, self.product, 100, reserved=10
        )
        self._update_product_qty_in_location(
            self.loc2, self.product, 50, reserved=0
        )
        self._update_product_qty_in_location(
            self.loc3, self.product, 50, reserved=0
        )
        self._update_product_qty_in_location(
            self.loc4, self.product, 100, reserved=0
        )
        move = self._create_picking_move(100)
        move.picking_id.action_assign()
        move_lines = move.move_line_ids
        self.assertRecordValues(
            move_lines, [{"location_id": self.loc4.id, "product_qty": 100}]
        )

    def test_no_packaging_pallet_reserved(self):
        self._update_product_qty_in_location(
            self.loc1, self.product, 100, reserved=10
        )
        self._update_product_qty_in_location(
            self.loc2, self.product, 50, reserved=0
        )
        self._update_product_qty_in_location(
            self.loc3, self.product, 50, reserved=0
        )
        self._update_product_qty_in_location(
            self.loc4, self.product, 100, reserved=0
        )
        move = self._create_picking_move(100)
        move.picking_id.action_assign()
        move_lines = move.move_line_ids
        self.assertRecordValues(
            move_lines,
            [
                {"location_id": self.loc1.id, "product_qty": 90},
                {"location_id": self.loc2.id, "product_qty": 10},
            ],
        )

    def test_remaining(self):
        self._setup_packagings(self.product, [("Pallet", 100), ("Box", 50)])
        self._update_product_qty_in_location(self.loc2, self.product, 100)
        self._update_product_qty_in_location(self.loc3, self.product, 50)
        self._update_product_qty_in_location(self.loc4, self.product, 10)
        move = self._create_picking_move(170)
        move.picking_id.action_assign()
        move_lines = move.move_line_ids
        self.assertRecordValues(
            move,
            [{"state": "partially_available", "reserved_availability": 160}],
        )
        self.assertRecordValues(
            move_lines,
            [
                {"location_id": self.loc2.id, "product_qty": 100},
                {"location_id": self.loc3.id, "product_qty": 50},
                {"location_id": self.loc4.id, "product_qty": 10},
            ],
        )
