# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta

from odoo.tests import Form, tagged

from odoo.addons.stock.tests.common import TestStockCommon


@tagged("post_install", "-at_install")
class TestReservationMethod(TestStockCommon):
    """
    Test backported from V15
    """

    def test_auto_assign_reservation_method(self):
        """Test different stock.picking.type reservation methods by:
        1. Create multiple delivery picking
        types with different reservation methods
        2. Create/confirm outgoing pickings for
        each of these picking types for a product not in stock
        3. Create/do an incoming picking
        that fulfills all of the outgoing pickings
        4. Check that only the correct outgoing pickings are auto_assigned
        5. Additionally check that auto-assignment
        at confirmation correctly works when products are in stock
        Note, default reservation method is
        expected to be covered by other tests.
        Also check reservation_dates are as expected
        """

        stock_location = self.env["stock.location"].browse(self.stock_location)
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.productA, stock_location
            ),
            0,
        )
        picking_type_out1 = (
            self.env["stock.picking.type"].browse(self.picking_type_out).copy()
        )
        picking_type_out2 = picking_type_out1.copy()
        picking_type_out3 = picking_type_out1.copy()
        picking_type_out4 = picking_type_out1.copy()
        picking_type_out1.reservation_method = "manual"
        picking_type_out2.reservation_method = "by_date"
        picking_type_out2.reservation_days_before = "1"
        picking_type_out3.reservation_method = "by_date"
        picking_type_out3.reservation_days_before = "10"
        picking_type_out4.reservation_method = "at_confirm"

        # 'manual' assign picking => should never auto-assign
        customer_picking1 = self.env["stock.picking"].create(
            {
                "name": "Delivery 1",
                "location_id": self.stock_location,
                "location_dest_id": self.customer_location,
                "picking_type_id": picking_type_out1.id,
            }
        )

        # 'by_date' picking w/ 1 day before scheduled date auto-assign
        # setting, set to 5 days in advance => shouldn't auto-assign
        customer_picking2 = customer_picking1.copy(
            {
                "name": "Delivery 2",
                "picking_type_id": picking_type_out2.id,
                "scheduled_date": customer_picking1.scheduled_date + timedelta(days=5),
            }
        )
        # 'by_date' picking w/ 10 days before scheduled date auto-assign
        # setting, set to 5 days in advance => should auto-assign
        customer_picking3 = customer_picking2.copy(
            {"name": "Delivery 3", "picking_type_id": picking_type_out3.id}
        )
        customer_picking4 = customer_picking3.copy(
            {"name": "Delivery 4", "picking_type_id": picking_type_out3.id}
        )
        # 'at_confirm' picking
        customer_picking5 = customer_picking1.copy(
            {"name": "Delivery 5", "picking_type_id": picking_type_out4.id}
        )

        # create their associated moves (needs to be in form
        # view so compute functions properly trigger)
        customer_picking1 = Form(customer_picking1)
        with customer_picking1.move_ids_without_package.new() as move:
            move.product_id = self.productA
            move.product_uom_qty = 10
        customer_picking1 = customer_picking1.save()

        customer_picking2 = Form(customer_picking2)
        with customer_picking2.move_ids_without_package.new() as move:
            move.product_id = self.productA
            move.product_uom_qty = 10
        customer_picking2 = customer_picking2.save()

        customer_picking3 = Form(customer_picking3)
        with customer_picking3.move_ids_without_package.new() as move:
            move.product_id = self.productA
            move.product_uom_qty = 10
        customer_picking3 = customer_picking3.save()

        customer_picking4 = Form(customer_picking4)
        with customer_picking4.move_ids_without_package.new() as move:
            move.product_id = self.productA
            move.product_uom_qty = 10
        customer_picking4 = customer_picking4.save()

        customer_picking5 = Form(customer_picking5)
        with customer_picking5.move_ids_without_package.new() as move:
            move.product_id = self.productA
            move.product_uom_qty = 10
        customer_picking5 = customer_picking5.save()

        customer_picking1.action_assign()
        customer_picking2.action_assign()
        customer_picking3.action_assign()
        self.assertEqual(
            customer_picking1.move_lines.reserved_availability,
            0,
            "There should be no products available to reserve yet.",
        )
        self.assertEqual(
            customer_picking2.move_lines.reserved_availability,
            0,
            "There should be no products available to reserve yet.",
        )
        self.assertEqual(
            customer_picking3.move_lines.reserved_availability,
            0,
            "There should be no products available to reserve yet.",
        )

        self.assertFalse(
            customer_picking1.move_lines.reservation_date,
            "Reservation Method: 'manual' shouldn't have a reservation_date",
        )
        self.assertEqual(
            customer_picking2.move_lines.reservation_date,
            (customer_picking2.scheduled_date - timedelta(days=1)).date(),
            "Reservation Method: 'by_date' should have a "
            "reservation_date = scheduled_date - reservation_days_before",
        )
        self.assertFalse(
            customer_picking5.move_lines.reservation_date,
            "Reservation Method: 'at_confirm' shouldn't "
            "have a reservation_date until confirmed",
        )

        # create supplier picking and move
        supplier_picking = self.env["stock.picking"].create(
            {
                "location_id": self.customer_location,
                "location_dest_id": self.stock_location,
                "picking_type_id": self.picking_type_in,
            }
        )
        supplier_move = self.env["stock.move"].create(
            {
                "name": "test_transit_1",
                "location_id": self.customer_location,
                "location_dest_id": self.stock_location,
                "product_id": self.productA.id,
                "product_uom": self.productA.uom_id.id,
                "product_uom_qty": 50.0,
                "picking_id": supplier_picking.id,
            }
        )
        supplier_move.quantity_done = 50
        supplier_picking._action_done()

        self.assertEqual(
            customer_picking1.move_lines.reserved_availability,
            0,
            "Reservation Method: 'manual' shouldn't ever auto-assign",
        )
        self.assertEqual(
            customer_picking2.move_lines.reserved_availability,
            0,
            "Reservation Method: 'by_date' shouldn't auto-assign "
            "when not within reservation date range",
        )
        self.assertEqual(
            customer_picking3.move_lines.reserved_availability,
            10,
            "Reservation Method: 'by_date' should auto-assign "
            "when within reservation date range",
        )
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.productA, stock_location
            ),
            40,
        )

        customer_picking4.action_confirm()
        customer_picking5.action_confirm()
        self.assertEqual(
            customer_picking4.move_lines.reserved_availability,
            10,
            "Reservation Method: 'by_date' should auto-assign "
            "when within reservation date range at confirmation",
        )
        self.assertEqual(
            customer_picking5.move_lines.reserved_availability,
            10,
            "Reservation Method: 'at_confirm' " "should auto-assign at confirmation",
        )
