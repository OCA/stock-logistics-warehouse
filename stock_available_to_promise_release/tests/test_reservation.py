# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import fields
from odoo.tests import common


class TestAvailableToPromiseRelease(common.SavepointCase):
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
            {"name": "Bin1", "location_id": cls.loc_stock.id}
        )

    def _create_picking_chain(
        self, wh, products=None, date=None, move_type="direct"
    ):
        """Create picking chain

        It runs the procurement group to create the moves required for
        a product. According to the WH, it creates the pick/pack/ship
        moves.

        Products must be a list of tuples (product, quantity) or
        (product, quantity, uom).
        One stock move will be created for each tuple.
        """

        if products is None:
            products = []

        group = self.env["procurement.group"].create(
            {
                "name": "TEST",
                "move_type": move_type,
                "partner_id": self.partner_delta.id,
            }
        )
        values = {
            "company_id": wh.company_id,
            "group_id": group,
            "date_planned": date or fields.Datetime.now(),
            "warehouse_id": wh,
        }

        for row in products:
            if len(row) == 2:
                product, qty = row
                uom = product.uom_id
            elif len(row) == 3:
                product, qty, uom = row
            else:
                raise ValueError(
                    "Expect (product, quantity, uom) or (product, quantity)"
                )
            self.env["procurement.group"].run(
                product, qty, uom, self.loc_customer, "TEST", "TEST", values
            )
        pickings = self._pickings_in_group(group)
        pickings.mapped("move_lines").write(
            {"date_priority": date or fields.Datetime.now()}
        )
        return pickings

    def _pickings_in_group(self, group):
        return self.env["stock.picking"].search([("group_id", "=", group.id)])

    def _update_qty_in_location(self, location, product, quantity):
        self.env["stock.quant"]._update_available_quantity(
            product, location, quantity
        )
        self.env["product.product"].invalidate_cache(
            fnames=[
                "qty_available",
                "virtual_available",
                "incoming_qty",
                "outgoing_qty",
            ]
        )

    def _prev_picking(self, picking):
        return picking.move_lines.move_orig_ids.picking_id

    def _out_picking(self, pickings):
        return pickings.filtered(lambda r: r.picking_type_code == "outgoing")

    def _deliver(self, picking):
        picking.action_assign()
        for line in picking.mapped("move_lines.move_line_ids"):
            line.qty_done = line.product_qty
        picking.action_done()

    def test_ordered_available_to_promise_value(self):
        self.wh.delivery_route_id.write(
            {"available_to_promise_defer_pull": True}
        )
        picking = self._out_picking(
            self._create_picking_chain(
                self.wh, [(self.product1, 5)], date=datetime(2019, 9, 2, 16, 0)
            )
        )
        picking2 = self._out_picking(
            self._create_picking_chain(
                self.wh, [(self.product1, 3)], date=datetime(2019, 9, 2, 16, 1)
            )
        )
        # we'll assign this one in the test, should deduct pick 1 and 2
        picking3 = self._out_picking(
            self._create_picking_chain(
                self.wh,
                [(self.product1, 20)],
                date=datetime(2019, 9, 3, 16, 0),
            )
        )
        # this one should be ignored when we'll assign pick 3 as it has
        # a later date
        picking4 = self._out_picking(
            self._create_picking_chain(
                self.wh,
                [(self.product1, 20)],
                date=datetime(2019, 9, 4, 16, 1),
            )
        )

        for pick in (picking, picking2, picking3, picking4):
            self.assertEqual(pick.state, "waiting")
            self.assertEqual(pick.move_lines.reserved_availability, 0.)

        self._update_qty_in_location(self.loc_bin1, self.product1, 20.)

        self.assertEqual(picking.move_lines._ordered_available_to_promise(), 5)
        self.assertEqual(
            picking2.move_lines._ordered_available_to_promise(), 3
        )
        self.assertEqual(
            picking3.move_lines._ordered_available_to_promise(), 12
        )
        self.assertEqual(
            picking4.move_lines._ordered_available_to_promise(), 0
        )

    def test_normal_chain(self):
        # usual scenario, without using the option to defer the pull
        pickings = self._create_picking_chain(self.wh, [(self.product1, 5)])
        self.assertEqual(len(pickings), 2, "expect stock->out + out->customer")
        self.assertRecordValues(
            pickings.sorted("id"),
            [
                {
                    "location_id": self.wh.lot_stock_id.id,
                    "location_dest_id": self.wh.wh_output_stock_loc_id.id,
                },
                {
                    "location_id": self.wh.wh_output_stock_loc_id.id,
                    "location_dest_id": self.loc_customer.id,
                },
            ],
        )

    def test_defer_creation(self):
        self.wh.delivery_route_id.write(
            {"available_to_promise_defer_pull": True}
        )

        self._update_qty_in_location(self.loc_bin1, self.product1, 20.)
        pickings = self._create_picking_chain(self.wh, [(self.product1, 5)])
        self.assertEqual(
            len(pickings), 1, "expect only the last out->customer"
        )
        cust_picking = pickings
        self.assertRecordValues(
            cust_picking,
            [
                {
                    "state": "waiting",
                    "location_id": self.wh.wh_output_stock_loc_id.id,
                    "location_dest_id": self.loc_customer.id,
                }
            ],
        )

        cust_picking.move_lines.release_available_to_promise()
        out_picking = self._pickings_in_group(pickings.group_id) - cust_picking

        self.assertRecordValues(
            out_picking,
            [
                {
                    "state": "assigned",
                    "location_id": self.wh.lot_stock_id.id,
                    "location_dest_id": self.wh.wh_output_stock_loc_id.id,
                }
            ],
        )

    def test_defer_creation_move_type_one(self):
        """Deliver all products at once"""
        self.wh.delivery_route_id.write(
            {"available_to_promise_defer_pull": True}
        )

        self._update_qty_in_location(self.loc_bin1, self.product1, 5.)
        pickings = self._create_picking_chain(
            self.wh, [(self.product1, 10.)], move_type="one"
        )
        self.assertEqual(
            len(pickings), 1, "expect only the last out->customer"
        )
        cust_picking = pickings
        self.assertRecordValues(
            cust_picking,
            [
                {
                    "state": "waiting",
                    "location_id": self.wh.wh_output_stock_loc_id.id,
                    "location_dest_id": self.loc_customer.id,
                }
            ],
        )

        cust_picking.move_lines.release_available_to_promise()
        # no chain picking should have been created because we would have a
        # partial and the move delivery type is "one"
        out_picking = self._pickings_in_group(pickings.group_id) - cust_picking
        self.assertFalse(out_picking)

        self._update_qty_in_location(self.loc_bin1, self.product1, 10.)
        # now, we have enough, the picking is created
        cust_picking.move_lines.release_available_to_promise()
        out_picking = self._pickings_in_group(pickings.group_id) - cust_picking
        self.assertRecordValues(
            out_picking,
            [
                {
                    "state": "assigned",
                    "location_id": self.wh.lot_stock_id.id,
                    "location_dest_id": self.wh.wh_output_stock_loc_id.id,
                }
            ],
        )

    def test_defer_creation_backorder(self):
        self.wh.delivery_route_id.write(
            {"available_to_promise_defer_pull": True}
        )

        self._update_qty_in_location(self.loc_bin1, self.product1, 7.)

        pickings = self._create_picking_chain(self.wh, [(self.product1, 20)])
        self.assertEqual(
            len(pickings), 1, "expect only the last out->customer"
        )
        cust_picking = pickings
        self.assertRecordValues(
            cust_picking,
            [
                {
                    "state": "waiting",
                    "location_id": self.wh.wh_output_stock_loc_id.id,
                    "location_dest_id": self.loc_customer.id,
                }
            ],
        )

        cust_picking.release_available_to_promise()

        out_picking = self._pickings_in_group(pickings.group_id) - cust_picking

        self.assertRecordValues(
            out_picking,
            [
                {
                    "state": "assigned",
                    "location_id": self.wh.lot_stock_id.id,
                    "location_dest_id": self.wh.wh_output_stock_loc_id.id,
                }
            ],
        )

        self.assertRecordValues(out_picking.move_lines, [{"product_qty": 7.}])

        self._deliver(out_picking)
        self.assertRecordValues(out_picking, [{"state": "done"}])

        self.assertRecordValues(cust_picking, [{"state": "assigned"}])
        self.assertRecordValues(
            cust_picking.move_lines,
            [
                {
                    "state": "assigned",
                    "product_qty": 7.,
                    "reserved_availability": 7.,
                    "procure_method": "make_to_order",
                },
                {
                    "state": "waiting",
                    "product_qty": 13.,
                    "reserved_availability": 0.,
                    "procure_method": "make_to_order",
                },
            ],
        )

        self._deliver(cust_picking)
        self.assertRecordValues(cust_picking, [{"state": "done"}])

        cust_backorder = (
            self._pickings_in_group(cust_picking.group_id)
            - cust_picking
            - out_picking
        )
        self.assertEqual(len(cust_backorder), 1)

        # nothing happen, no stock
        self.assertEqual(
            len(self._pickings_in_group(cust_picking.group_id)), 3
        )
        cust_backorder.release_available_to_promise()
        self.assertEqual(
            len(self._pickings_in_group(cust_picking.group_id)), 3
        )

        # We add stock, so now the release must create the next
        # chained move
        self._update_qty_in_location(self.loc_bin1, self.product1, 30)
        cust_backorder.release_available_to_promise()
        out_backorder = (
            self._pickings_in_group(cust_picking.group_id)
            - cust_backorder
            - cust_picking
            - out_picking
        )
        self.assertRecordValues(
            out_backorder.move_lines,
            [
                {
                    "state": "assigned",
                    "product_qty": 13.,
                    "reserved_availability": 13.,
                    "procure_method": "make_to_stock",
                    "location_id": self.wh.lot_stock_id.id,
                    "location_dest_id": self.wh.wh_output_stock_loc_id.id,
                }
            ],
        )

    def test_defer_multi_move(self):
        self.wh.delivery_route_id.write(
            {"available_to_promise_defer_pull": True}
        )

        self._update_qty_in_location(self.loc_bin1, self.product2, 10.)

        pickings = self._create_picking_chain(
            self.wh, [(self.product1, 20), (self.product2, 10)]
        )
        self.assertEqual(
            len(pickings), 1, "expect only the last out->customer"
        )
        cust_picking = pickings
        self.assertRecordValues(
            cust_picking,
            [
                {
                    "state": "waiting",
                    "location_id": self.wh.wh_output_stock_loc_id.id,
                    "location_dest_id": self.loc_customer.id,
                }
            ],
        )

        cust_picking.release_available_to_promise()

        out_picking = self._pickings_in_group(pickings.group_id) - cust_picking

        self.assertRecordValues(
            out_picking,
            [
                {
                    "state": "assigned",
                    "location_id": self.wh.lot_stock_id.id,
                    "location_dest_id": self.wh.wh_output_stock_loc_id.id,
                }
            ],
        )

        self.assertRecordValues(
            out_picking.move_lines,
            [{"product_qty": 10., "product_id": self.product2.id}],
        )

    def test_defer_creation_uom(self):
        self.wh.delivery_route_id.write(
            {"available_to_promise_defer_pull": True}
        )

        self._update_qty_in_location(self.loc_bin1, self.product1, 12.)
        uom_dozen = self.env.ref("uom.product_uom_dozen")
        pickings = self._create_picking_chain(
            self.wh,
            # means 24 products
            [(self.product1, 2, uom_dozen)],
        )
        self.assertEqual(
            len(pickings), 1, "expect only the last out->customer"
        )
        cust_picking = pickings
        self.assertRecordValues(
            cust_picking,
            [
                {
                    "state": "waiting",
                    "location_id": self.wh.wh_output_stock_loc_id.id,
                    "location_dest_id": self.loc_customer.id,
                }
            ],
        )
        self.assertRecordValues(
            cust_picking.move_lines,
            [
                {
                    "state": "waiting",
                    "product_uom": uom_dozen.id,
                    "product_qty": 24.,
                    "product_uom_qty": 2.,
                    "ordered_available_to_promise": 12.,
                }
            ],
        )

        cust_picking.move_lines.release_available_to_promise()
        out_picking = self._pickings_in_group(pickings.group_id) - cust_picking

        self.assertRecordValues(
            out_picking.move_lines,
            [
                {
                    "state": "assigned",
                    "product_qty": 12.,
                    "reserved_availability": 1.,
                    "product_uom_qty": 1.,
                }
            ],
        )

    def test_mto_picking(self):
        self.wh.delivery_route_id.write(
            {"available_to_promise_defer_pull": True}
        )
        # TODO a MTO picking should work normally
