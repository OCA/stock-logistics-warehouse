# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import namedtuple

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

ShortMoveInfo = namedtuple("ShortMoveInfo", ["product", "location_dest", "qty"])


class TestStockMove(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        Data:
            2 products: product_1, product_2
            1 new warehouse: warehouse_1
            2 new locations: location_1 and location_2 are child of
                             warehouse_1's stock location and without
                             restriction
            stock:
                * 50 product_1 in location_1
                * 0 product_2 en stock
        """
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        Product = cls.env["product.product"]
        cls.product_1 = Product.create(
            {"name": "Wood", "type": "product", "uom_id": cls.uom_unit.id}
        )
        cls.product_2 = Product.create(
            {"name": "Stone", "type": "product", "uom_id": cls.uom_unit.id}
        )

        # Warehouses
        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
                "code": "BWH",
            }
        )

        # Locations
        cls.location_1 = cls.env["stock.location"].create(
            {
                "name": "TestLocation1",
                "posx": 3,
                "location_id": cls.warehouse_1.lot_stock_id.id,
            }
        )

        cls.location_2 = cls.env["stock.location"].create(
            {
                "name": "TestLocation2",
                "posx": 4,
                "location_id": cls.warehouse_1.lot_stock_id.id,
            }
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")

        # partner
        cls.partner_1 = cls.env["res.partner"].create(
            {"name": "ACSONE SA/NV", "email": "info@acsone.eu"}
        )

        # picking type
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")

        # Inventory Add product_1 to location_1
        cls._change_product_qty(cls.product_1, cls.location_1, 50)
        cls.StockMove = cls.env["stock.move"]
        cls.StockPicking = cls.env["stock.picking"]

    @classmethod
    def _change_product_qty(cls, product, location, qty):
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "inventory_quantity": qty,
                "location_id": location.id,
            }
        )._apply_inventory()

    def _get_products_in_location(self, location):
        return (
            self.env["stock.quant"]
            .search([("location_id", "=", location.id)])
            .mapped("product_id")
        )

    def _create_and_assign_picking(self, short_move_infos, location_dest=None):
        location_dest = location_dest or self.location_1
        picking_in = self.StockPicking.create(
            {
                "partner_id": self.partner_1.id,
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": location_dest.id,
            }
        )
        for move_info in short_move_infos:
            self.StockMove.create(
                {
                    "name": move_info.product.name,
                    "product_id": move_info.product.id,
                    "product_uom_qty": move_info.qty,
                    "product_uom": move_info.product.uom_id.id,
                    "picking_id": picking_in.id,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": move_info.location_dest.id,
                }
            )
        picking_in.action_confirm()
        return picking_in

    def _process_picking(self, picking):
        picking.action_assign()
        for line in picking.move_line_ids:
            line.qty_done = line.reserved_qty
        picking.button_validate()

    def test_00(self):
        """
        Data:
            location_1 without product_restriction
            location_1 with 50 product_1
        Test case:
            Add qty of product_2 into location_1
        Expected result:
            The location contains the 2 products
        """
        self.assertEqual(
            self.product_1, self._get_products_in_location(self.location_1)
        )
        self._change_product_qty(self.product_2, self.location_1, 10)
        self.assertEqual(
            self.product_1 | self.product_2,
            self._get_products_in_location(self.location_1),
        )

    def test_01(self):
        """
        Data:
            location_1 with same product restriction
            location_1 with 50 product_1
        Test case:
            Add qty of product_2 into location_1
        Expected result:
            ValidationError
        """
        self.assertEqual(
            self.product_1, self._get_products_in_location(self.location_1)
        )
        self.location_1.specific_product_restriction = "same"
        self.location_1.flush_recordset()
        with self.assertRaises(ValidationError):
            self._change_product_qty(self.product_2, self.location_1, 10)

    def test_02(self):
        """
        Data:
            location_2 without product nor product restriction
            a picking with two move with destination location_2
        Test case:
            Process the picking
        Expected result:
            The two product are into location 2
        """
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_2,
                    qty=2,
                ),
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_2,
                    qty=2,
                ),
            ],
            location_dest=self.location_2,
        )
        self._process_picking(picking)
        self.assertEqual(
            self.product_1 | self.product_2,
            self._get_products_in_location(self.location_2),
        )

    def test_03(self):
        """
        Data:
            location_2 without product but with product restriction = 'same'
            a picking with two move with destination location_2
        Test case:
            Process the picking
        Expected result:
            ValidationError
        """
        self.location_2.specific_product_restriction = "same"
        self.location_2.flush_recordset()
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_2,
                    qty=2,
                ),
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_2,
                    qty=2,
                ),
            ],
            location_dest=self.location_2,
        )
        with self.assertRaises(ValidationError):
            self._process_picking(picking)

    def test_04(self):
        """
        Data:
            location_1 with product_1 and wihout product restriction = 'same'
            a picking with two moves:
             * product_1 -> location_1,
             * product_2 -> location_1
        Test case:
            Process the picking
        Expected result:
            We now have two product into the same location
        """
        self.assertEqual(
            self.product_1,
            self._get_products_in_location(self.location_1),
        )
        self.location_1.specific_product_restriction = "any"
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_1,
                    qty=2,
                ),
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_1,
                    qty=2,
                ),
            ],
            location_dest=self.location_1,
        )
        self._process_picking(picking)
        self.assertEqual(
            self.product_1 | self.product_2,
            self._get_products_in_location(self.location_1),
        )

    def test_05(self):
        """
        Data:
            location_1 with product_1 but with product restriction = 'same'
            a picking with one move: product_2 -> location_1
        Test case:
            Process the picking
        Expected result:
            ValidationError
        """

        self.assertEqual(
            self.product_1,
            self._get_products_in_location(self.location_1),
        )
        self.location_1.specific_product_restriction = "same"
        self.location_1.invalidate_recordset()
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_1,
                    qty=2,
                ),
            ],
            location_dest=self.location_1,
        )
        with self.assertRaises(ValidationError):
            self._process_picking(picking)
