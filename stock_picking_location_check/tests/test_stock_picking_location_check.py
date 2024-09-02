# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockPickingLocationCheck(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "test product"})
        cls.location1 = cls._create_location(cls, "location 1")
        cls.location2 = cls._create_location(cls, "location 2")
        cls.location2_1 = cls._create_location(cls, "location 2-1", cls.location2)
        cls.location2_1_1 = cls._create_location(cls, "location 2-1-1", cls.location2_1)
        cls.location3 = cls._create_location(cls, "location 3")
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_internal").id,
                "location_id": cls.location1.id,
                "location_dest_id": cls.location2.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "name": cls.product.name,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.location1.id,
                "location_dest_id": cls.location2.id,
                "picking_id": cls.picking.id,
                "product_uom_qty": 10,
                "state": "assigned",
            }
        )
        cls.move_line = cls.env["stock.move.line"].create(
            {
                "move_id": cls.move.id,
                "product_id": cls.product.id,
                "product_uom_id": cls.product.uom_id.id,
                "location_id": cls.location1.id,
                "location_dest_id": cls.location2.id,
                "picking_id": cls.picking.id,
                "qty_done": 10,
            }
        )

    def _create_location(self, name, parent_location=None):
        vals = {"name": name, "usage": "internal"}
        if parent_location:
            vals["location_id"] = parent_location.id
        return self.env["stock.location"].create(vals)

    def test_locations_no_inconsistency(self):
        self.picking.button_validate()

    def test_locations_no_inconsistency_recursive(self):
        # Destination location of the move line is a grand child of that of the picking
        self.move_line.location_dest_id = self.location2_1_1.id
        self.picking.button_validate()

    def test_locations_with_inconsistency(self):
        # Make source locations inconsistent between picking and move line
        self.picking.location_dest_id = self.location3
        with self.assertRaises(UserError):
            self.picking.button_validate()
        self.picking.location_dest_id = self.location2
        # Make destination locations inconsistent between picking and move line
        self.picking.location_id = self.location3
        with self.assertRaises(UserError):
            self.picking.button_validate()
        self.picking.allow_location_inconsistency = True
        self.picking.button_validate()
