# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tests import common


class TestVirtualReservation(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "WHTEST",
            }
        )
        cls.loc_stock = cls.wh.lot_stock_id
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.product1 = cls.env["product.product"].create(
            {"name": "Product 1", "type": "product"}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "Product 2", "type": "product"}
        )
        cls.partner_delta = cls.env.ref("base.res_partner_4")
        cls.loc_bin1 = cls.env["stock.location"].create(
            {"name": "Bin1", "location_id": cls.loc_stock.id, "kind": "bin"}
        )

    def _create_picking(self, wh, products=None, date=None):
        """Create picking

        Products must be a list of tuples (product, quantity).
        One stock move will be created for each tuple.
        """

        if products is None:
            products = []

        values = {
            "location_id": wh.lot_stock_id.id,
            "location_dest_id": wh.wh_output_stock_loc_id.id,
            "partner_id": self.partner_delta.id,
            "picking_type_id": wh.pick_type_id.id,
        }

        if date:
            values["date"] = date
        picking = self.env["stock.picking"].create(values)

        for product, qty in products:
            values = {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "picking_id": picking.id,
                "location_id": wh.lot_stock_id.id,
                "location_dest_id": wh.wh_output_stock_loc_id.id,
                "state": "confirmed",
            }
            if date:
                values["date"] = date
            self.env["stock.move"].create(values)
        return picking

    def _update_qty_in_location(self, location, product, quantity):
        self.env["stock.quant"]._update_available_quantity(
            product, location, quantity
        )

    def test_reservation(self):
        picking = self._create_picking(
            self.wh, [(self.product1, 5)], date=datetime(2019, 9, 2, 16)
        )
        picking2 = self._create_picking(
            self.wh, [(self.product1, 3)], date=datetime(2019, 9, 2, 16)
        )
        # we'll assign this one in the test, should deduct pick 1 and 2
        picking3 = self._create_picking(
            self.wh, [(self.product1, 20)], date=datetime(2019, 9, 3, 16)
        )
        # this one should be ignored when we'll assign pick 3 as it has
        # a later date
        picking4 = self._create_picking(
            self.wh, [(self.product1, 20)], date=datetime(2019, 9, 4, 16)
        )

        for pick in (picking, picking2, picking3, picking4):
            self.assertEqual(pick.state, "confirmed")
            self.assertEqual(pick.move_lines.reserved_availability, 0.)

        self._update_qty_in_location(self.loc_bin1, self.product1, 20.)

        picking3.action_assign()
        self.assertEqual(picking.move_lines.reserved_availability, 0.)
        self.assertEqual(
            picking3.move_lines.reserved_availability,
            12.0,
            "12 expected as 8 are virtually reserved for the first pickings",
        )
