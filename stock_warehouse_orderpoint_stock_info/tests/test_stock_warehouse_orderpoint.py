# Copyright 2016 OdooMRP Team
# Copyright 2016 AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2016-17 ForgeFlow, S.L.
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockWarehouseOrderpoint(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Get required Model
        cls.reordering_rule_model = cls.env["stock.warehouse.orderpoint"]
        cls.stock_move_model = cls.env["stock.move"]
        cls.product_model = cls.env["product.product"]
        cls.product_ctg_model = cls.env["product.category"]

        # Get required Model data
        cls.product_uom = cls.env.ref("uom.product_uom_unit")
        cls.dest_location = cls.env.ref("stock.stock_location_stock")
        cls.location = cls.env.ref("stock.stock_location_locations_partner")
        cls.picking = cls.env.ref("stock.picking_type_in")

        # Create product category and product
        cls.product_ctg = cls.product_ctg_model.create({"name": "test_product_ctg"})
        cls.product = cls.product_model.create(
            {
                "name": "Test Product",
                "categ_id": cls.product_ctg.id,
                "type": "product",
                "uom_id": cls.product_uom.id,
            }
        )

        # Create Reordering Rule
        cls.reordering_record = cls.reordering_rule_model.create(
            {
                "name": "Reordering Rule",
                "product_id": cls.product.id,
                "product_min_qty": "1",
                "product_max_qty": "5",
                "qty_multiple": "1",
                "location_id": cls.dest_location.id,
            }
        )

    def create_stock_move(self):
        """Create a Stock Move."""
        move = self.stock_move_model.create(
            {
                "name": "Reordering Product",
                "product_id": self.product.id,
                "product_uom": self.product_uom.id,
                "product_uom_qty": "10.0",
                "picking_type_id": self.picking.id,
                "location_id": self.location.id,
                "location_dest_id": self.dest_location.id,
            }
        )
        move._action_confirm()
        return move

    def test_product_qty(self):
        """Tests the product quantity in the Reordering rules"""
        # Create & process moves to test the product quantity
        move = self.create_stock_move()
        self.reordering_record.refresh()
        self.assertEqual(
            self.reordering_record.incoming_location_qty,
            self.product.incoming_qty,
            "Incoming Qty does not match",
        )
        self.assertEqual(
            self.reordering_record.virtual_location_qty,
            self.product.virtual_available,
            "Virtual Qty does not match",
        )
        move._action_done()
        self.reordering_record.refresh()
        self.assertEqual(
            self.reordering_record.product_location_qty,
            self.product.qty_available,
            "Available Qty does not match",
        )
        self.assertEqual(
            self.reordering_record.virtual_location_qty,
            self.product.virtual_available,
            "Virtual Qty does not match",
        )
