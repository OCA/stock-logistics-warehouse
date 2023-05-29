# Copyright 2023 Raumschmiede (http://www.raumschmiede.de)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from collections import namedtuple

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase

from odoo.addons.stock_location_package_restriction.models.stock_location import (
    MULTIPACKAGE,
    NORESTRICTION,
    SINGLEPACKAGE,
)

ShortMoveInfo = namedtuple(
    "ShortMoveInfo", ["product", "location_dest", "qty", "package_id"]
)


class TestStockMove(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """
        Data:
            2 products: product_1, product_2
            2 packages: pack_1, pack_2
            1 new warehouse: warehouse1
            2 new locations: location1 and location2 are children of
                             warehouse1's stock location and without
                             restriction
            stock:
                * 50 product_1 in location_1
                * 0 product_2 in stock
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

        # Packages:
        Package = cls.env["stock.quant.package"]
        cls.pack_1 = Package.create({"name": "Package 1"})
        cls.pack_2 = Package.create({"name": "Package 2"})

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")

        # partner
        cls.partner_1 = cls.env["res.partner"].create(
            {"name": "Raumschmiede.de", "email": "info@raumschmiede.de"}
        )

        # picking type
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")

        cls.StockMove = cls.env["stock.move"]
        cls.StockPicking = cls.env["stock.picking"]

    @classmethod
    def _change_product_qty(cls, product, location, package, qty):
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "package_id": package.id,
                "inventory_quantity": qty,
                "location_id": location.id,
            }
        )

    def _get_package_in_location(self, location):
        return (
            self.env["stock.quant"]
            .search([("location_id", "=", location.id)])
            .mapped("package_id")
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
        for move_info in short_move_infos:
            line = picking_in.move_line_ids.filtered(
                lambda x: x.product_id.id == move_info.product.id
            )
            if line:
                line.result_package_id = move_info.package_id
        return picking_in

    def _process_picking(self, picking):
        picking.action_assign()
        for line in picking.move_line_ids:
            line.qty_done = line.product_qty
        picking.button_validate()

    def test_00(self):
        """
        Data:
            location_1 without package_restriction
            location_1 with 50 product_1 and pack_1
        Test case:
            Add qty of product_2 into location_1 with pack_2
        Expected result:
            The location contains the 2 products in 2 different packages
        """
        # Inventory Add product_1 to location_1
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        self.assertEqual(self.pack_1, self._get_package_in_location(self.location_1))

        self._change_product_qty(self.product_2, self.location_1, self.pack_2, 10)
        self.assertEqual(
            self.pack_1 | self.pack_2,
            self._get_package_in_location(self.location_1),
        )

    def test_01(self):
        """
        Data:
            location_1 with single package restriction
            location_1 with 50 product_1 and pack_1
        Test case:
            Add qty of product_2 into location_1 with pack_2
        Expected result:
            ValidationError
        """
        # Inventory Add product_1 to location_1
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        self.assertEqual(self.pack_1, self._get_package_in_location(self.location_1))
        self.location_1.package_restriction = SINGLEPACKAGE
        with self.assertRaises(ValidationError):
            self._change_product_qty(self.product_2, self.location_1, self.pack_2, 10)

    def test_02(self):
        """
        Data:
            location_2 without product nor product restriction
            a picking with two move with destination location_2
        Test case:
            Process the picking
        Expected result:
            The two packages are on location 2
        """
        self.location_2.package_restriction = MULTIPACKAGE
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_2,
                    qty=2,
                    package_id=self.pack_1,
                ),
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_2,
                    qty=4,
                    package_id=self.pack_2,
                ),
            ],
            location_dest=self.location_2,
        )
        self._process_picking(picking)
        self.assertEqual(
            self.pack_1 | self.pack_2,
            self._get_package_in_location(self.location_2),
        )

    def test_03(self):
        """
        Data:
            location_2 without package but with package restriction = 'single package'
            a picking with two move with destination location_2
        Test case:
            Process the picking
        Expected result:
            ValidationError
        """
        self.location_2.package_restriction = SINGLEPACKAGE
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_2,
                    qty=2,
                    package_id=self.pack_1,
                ),
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_2,
                    qty=2,
                    package_id=self.pack_2,
                ),
            ],
            location_dest=self.location_2,
        )
        with self.assertRaises(ValidationError):
            self._process_picking(picking)

    def test_04(self):
        """
        Data:
            location_1 with product_1 and without product restriction = 'single package'
            a picking with two moves:
             * product_1 -> location_1,
             * product_2 -> location_1
        Test case:
            Process the picking
        Expected result:
            We now have two products into the same location
        """
        # Inventory Add product_1 to location_1
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        self.assertEqual(
            self.pack_1,
            self._get_package_in_location(self.location_1),
        )
        self.location_1.package_restriction = NORESTRICTION
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_1,
                    location_dest=self.location_1,
                    qty=2,
                    package_id=self.pack_1,
                ),
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_1,
                    qty=2,
                    package_id=self.pack_2,
                ),
            ],
            location_dest=self.location_1,
        )
        self._process_picking(picking)
        self.assertEqual(
            self.pack_1 | self.pack_2,
            self._get_package_in_location(self.location_1),
        )

    def test_05(self):
        """
        Data:
            location_1 with product_1 but with product restriction = 'single package'
            a picking with one move: product_2 -> location_1
        Test case:
            Process the picking
        Expected result:
            ValidationError
        """
        # Inventory Add product_1 to location_1
        self._change_product_qty(self.product_1, self.location_1, self.pack_1, 50)
        self.assertEqual(
            self.pack_1,
            self._get_package_in_location(self.location_1),
        )
        self.location_1.package_restriction = SINGLEPACKAGE
        picking = self._create_and_assign_picking(
            [
                ShortMoveInfo(
                    product=self.product_2,
                    location_dest=self.location_1,
                    qty=2,
                    package_id=self.pack_2,
                ),
            ],
            location_dest=self.location_1,
        )
        with self.assertRaises(ValidationError):
            self._process_picking(picking)
