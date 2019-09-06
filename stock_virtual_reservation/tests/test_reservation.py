# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import fields
from odoo.tests import common


class TestVirtualReservation(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh = cls.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
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

    def _create_picking_chain(self, wh, products=None, date=None):
        """Create picking chain

        It runs the procurement group to create the moves required for
        a product. According to the WH, it creates the pick/pack/ship
        moves.

        Products must be a list of tuples (product, quantity).
        One stock move will be created for each tuple.
        """

        if products is None:
            products = []

        group = self.env["procurement.group"].create(
            {
                "name": "TEST",
                "move_type": "one",
                "partner_id": self.partner_delta.id,
            }
        )
        values = {
            "company_id": wh.company_id,
            "group_id": group,
            "date_planned": date or fields.Datetime.now(),
            "warehouse_id": wh,
            "partner_id": self.partner_delta,
        }

        for product, qty in products:
            self.env["procurement.group"].run(
                product,
                qty,
                product.uom_id,
                self.loc_customer,
                "TEST",
                "TEST",
                values,
            )
        return self.env["stock.picking"].search([("group_id", "=", group.id)])

    def _update_qty_in_location(self, location, product, quantity):
        self.env["stock.quant"]._update_available_quantity(
            product, location, quantity
        )

    def _prev_picking(self, picking):
        return picking.move_lines.move_orig_ids.picking_id

    def _deliver(self, picking):
        picking.action_assign()
        for line in picking.mapped("move_lines.move_line_ids"):
            line.qty_done = line.product_qty
        picking.action_done()

    def test_reservation(self):
        picking = self._create_picking_chain(
            self.wh, [(self.product1, 5)], date=datetime(2019, 9, 2, 16, 0)
        ).filtered(lambda r: r.picking_type_code == "outgoing")
        picking2 = self._create_picking_chain(
            self.wh, [(self.product1, 3)], date=datetime(2019, 9, 2, 16, 1)
        ).filtered(lambda r: r.picking_type_code == "outgoing")
        # we'll assign this one in the test, should deduct pick 1 and 2
        picking3 = self._create_picking_chain(
            self.wh, [(self.product1, 20)], date=datetime(2019, 9, 3, 16, 0)
        ).filtered(lambda r: r.picking_type_code == "outgoing")
        # this one should be ignored when we'll assign pick 3 as it has
        # a later date
        picking4 = self._create_picking_chain(
            self.wh, [(self.product1, 20)], date=datetime(2019, 9, 4, 16, 1)
        ).filtered(lambda r: r.picking_type_code == "outgoing")

        for pick in (picking, picking2, picking3, picking4):
            # self.assertEqual(pick.move_lines.virtual_reserved_qty, 0)
            self.assertEqual(pick.state, "waiting")
            self.assertEqual(pick.move_lines.reserved_availability, 0.)

        self._update_qty_in_location(self.loc_bin1, self.product1, 20.)

        self.assertEqual(picking.move_lines.virtual_reserved_qty, 5)
        self.assertEqual(picking2.move_lines.virtual_reserved_qty, 3)
        self.assertEqual(picking3.move_lines.virtual_reserved_qty, 12)
        self.assertEqual(picking4.move_lines.virtual_reserved_qty, 0)

        # Take care of the stock->output
        self._deliver(self._prev_picking(picking3))

        # Now, output->customer should be partially reserved, according
        # to the virtual reservation
        self.assertEqual(picking.move_lines.reserved_availability, 0.)
        self.assertEqual(
            picking3.move_lines.reserved_availability,
            12.0,
            "12 expected as 8 are virtually reserved for the first pickings",
        )
