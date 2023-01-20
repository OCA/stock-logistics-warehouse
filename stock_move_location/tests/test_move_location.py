# Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError

from .test_common import TestsCommon


class TestMoveLocation(TestsCommon):
    def setUp(self):
        super().setUp()
        self.setup_product_amounts()

    def test_move_location_wizard(self):
        """Test a simple move."""
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.onchange_origin_location()
        wizard.action_move_location()
        self.check_product_amount(self.product_no_lots, self.internal_loc_1, 0)
        self.check_product_amount(self.product_lots, self.internal_loc_1, 0, self.lot1)
        self.check_product_amount(self.product_lots, self.internal_loc_1, 0, self.lot2)
        self.check_product_amount(self.product_lots, self.internal_loc_1, 0, self.lot3)
        self.check_product_amount(
            self.product_package, self.internal_loc_1, 0, self.lot4, self.package1
        )
        self.check_product_amount(
            self.product_package,
            self.internal_loc_1,
            0,
            self.lot5,
            self.package2,
            self.partner,
        )
        self.check_product_amount(self.product_no_lots, self.internal_loc_2, 123)
        self.check_product_amount(self.product_lots, self.internal_loc_2, 1, self.lot1)
        self.check_product_amount(self.product_lots, self.internal_loc_2, 1, self.lot2)
        self.check_product_amount(self.product_lots, self.internal_loc_2, 1, self.lot3)
        self.check_product_amount(
            self.product_package, self.internal_loc_2, 1, self.lot4, self.package1
        )
        self.check_product_amount(
            self.product_package,
            self.internal_loc_2,
            1,
            self.lot5,
            self.package2,
            self.partner,
        )

    def test_move_location_wizard_amount(self):
        """Can't move more than exists."""
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.onchange_origin_location()
        with self.assertRaises(ValidationError):
            wizard.stock_move_location_line_ids[0].move_quantity += 1

    def test_move_location_wizard_ignore_reserved(self):
        """Can't move more than exists."""
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.onchange_origin_location()
        # reserve some quants
        self.quant_obj._update_reserved_quantity(
            self.product_no_lots, self.internal_loc_1, 50
        )
        self.quant_obj._update_reserved_quantity(
            self.product_lots, self.internal_loc_1, 1, lot_id=self.lot1
        )
        # doesn't care about reservations, everything is moved
        wizard.action_move_location()
        self.check_product_amount(self.product_no_lots, self.internal_loc_1, 0)
        self.check_product_amount(self.product_no_lots, self.internal_loc_2, 123)
        self.check_product_amount(self.product_lots, self.internal_loc_2, 1, self.lot1)

    def test_wizard_clear_lines(self):
        """Test lines getting cleared properly."""
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.onchange_origin_location()
        self.assertEqual(len(wizard.stock_move_location_line_ids), 6)
        wizard._onchange_destination_location_id()
        self.assertEqual(len(wizard.stock_move_location_line_ids), 6)
        dest_location_line = wizard.stock_move_location_line_ids.mapped(
            "destination_location_id"
        )
        self.assertEqual(dest_location_line, wizard.destination_location_id)
        wizard._onchange_origin_location_id()
        self.assertEqual(len(wizard.stock_move_location_line_ids), 0)

    def test_planned_transfer(self):
        """Test planned transfer."""
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.onchange_origin_location()
        wizard = wizard.with_context({"planned": True})
        wizard.action_move_location()
        picking = wizard.picking_id
        self.assertEqual(picking.state, "assigned")
        self.assertEqual(len(picking.move_line_ids), 6)
        self.assertEqual(
            sorted(picking.move_line_ids.mapped("product_uom_qty")),
            [1, 1, 1, 1, 1, 123],
        )

    def test_quant_transfer(self):
        """Test quants transfer."""
        quants = self.product_lots.stock_quant_ids
        wizard = self.wizard_obj.with_context(
            active_model="stock.quant",
            active_ids=quants.ids,
            origin_location_disable=True,
        ).create(
            {
                "origin_location_id": quants[:1].location_id.id,
                "destination_location_id": self.internal_loc_2.id,
            }
        )
        lines = wizard.stock_move_location_line_ids
        self.assertEqual(len(lines), 3)
        wizard.onchange_origin_location()
        self.assertEqual(len(lines), 3)
        wizard.destination_location_id = self.internal_loc_1
        wizard._onchange_destination_location_id()
        self.assertEqual(lines.mapped("destination_location_id"), self.internal_loc_1)
        wizard.origin_location_id = self.internal_loc_2
        wizard._onchange_destination_location_id()
        self.assertEqual(len(lines), 3)

    def test_readonly_location_computation(self):
        """Test that origin_location_disable and destination_location_disable
        are computed correctly."""
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        # locations are editable.
        self.assertFalse(wizard.origin_location_disable)
        self.assertFalse(wizard.destination_location_disable)
        # Disable edit mode:
        wizard.edit_locations = False
        self.assertTrue(wizard.origin_location_disable)
        self.assertTrue(wizard.destination_location_disable)

    def test_picking_type_action_dummy(self):
        """Test that no error is raised from actions."""
        pick_type = self.env.ref("stock.picking_type_internal")
        pick_type.action_move_location()

    def test_wizard_with_putaway_strategy(self):
        """Test that Putaway strategies are being applied."""
        self._create_putaway_for_product(
            self.product_no_lots, self.internal_loc_2, self.internal_loc_2_shelf
        )
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.apply_putaway_strategy = True
        wizard.onchange_origin_location()
        putaway_line = wizard.stock_move_location_line_ids.filtered(
            lambda p: p.product_id == self.product_no_lots
        )[0]
        self.assertEqual(
            putaway_line.destination_location_id, self.internal_loc_2_shelf
        )

        # Actually commit the wizard and check stock.move.line.location_dest_id
        ret = wizard.action_move_location()
        picking = self.env["stock.picking"].browse([ret["res_id"]])
        putaway_move_line = picking.move_line_ids.filtered(
            lambda l: l.product_id == self.product_no_lots
        )[0]
        self.assertEqual(putaway_move_line.location_dest_id, self.internal_loc_2_shelf)

    def test_delivery_order_assignation_after_transfer(self):
        """
        Make sure using the wizard doesn't break assignation on delivery orders
        """
        delivery_order_type = self.env.ref("stock.picking_type_out")
        internal_transfer_type = self.env.ref("stock.picking_type_internal")
        wh_stock_shelf_1 = self.env.ref("stock.stock_location_components")
        wh_stock_shelf_2 = self.env.ref("stock.stock_location_14")
        wh_stock_shelf_3 = wh_stock_shelf_1.copy({"name": "Shelf 3"})

        # Create some quants
        self.set_product_amount(
            self.product_lots, wh_stock_shelf_1, 100, lot_id=self.lot1
        )

        # Create and assign a delivery picking to reserve some quantities
        delivery_picking = self._create_picking(delivery_order_type)
        delivery_move = self.env["stock.move"].create(
            {
                "name": "Delivery move",
                "product_id": self.product_lots.id,
                "product_uom_qty": 20.0,
                "product_uom": self.product_lots.uom_id.id,
                "location_id": delivery_picking.location_id.id,
                "location_dest_id": delivery_picking.location_dest_id.id,
                "picking_id": delivery_picking.id,
            }
        )
        delivery_picking.action_confirm()
        self.assertEqual(delivery_picking.state, "confirmed")
        delivery_picking.action_assign()
        self.assertEqual(delivery_picking.state, "assigned")

        # Move all quantities to other location using module's wizard
        wizard = self._create_wizard(wh_stock_shelf_1, wh_stock_shelf_2)
        wizard.onchange_origin_location()
        wizard.action_move_location()
        self.assertEqual(delivery_picking.state, "assigned")

        # Do a planned transfer to move quantities to other location
        #  without using module's wizard
        internal_picking = self._create_picking(internal_transfer_type)
        internal_picking.write(
            {"location_id": wh_stock_shelf_2, "location_dest_id": wh_stock_shelf_3.id}
        )
        self.env["stock.move"].create(
            {
                "name": "Internal move",
                "product_id": self.product_lots.id,
                "product_uom_qty": 100.0,
                "product_uom": self.product_lots.uom_id.id,
                "location_id": internal_picking.location_id.id,
                "location_dest_id": internal_picking.location_dest_id.id,
                "picking_id": internal_picking.id,
            }
        )
        # Unreserve quantity on the delivery to allow moving the quantity
        delivery_picking.do_unreserve()
        self.assertEqual(delivery_picking.state, "confirmed")
        internal_picking.action_confirm()
        internal_picking.action_assign()
        internal_picking.move_line_ids.qty_done = (
            internal_picking.move_line_ids.product_uom_qty
        )
        internal_picking.button_validate()
        self.assertEqual(internal_picking.state, "done")
        # Assign the delivery must work
        delivery_picking.action_assign()
        self.assertEqual(delivery_picking.state, "assigned")
        # The old reserved quantities must be in new location after confirm wizard
        self.assertEqual(len(delivery_move.move_line_ids), 1)
        self.assertEqual(delivery_move.move_line_ids.product_uom_qty, 20.0)
        self.assertEqual(delivery_move.move_line_ids.location_id, wh_stock_shelf_3)

    def test_wizard_available_quantity_exeptions(self):
        """
        Make sure _get_available_quantity returns 0,0 on stock exceptions.
        """
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.onchange_origin_location()
        first_line = wizard.stock_move_location_line_ids[0]

        # Check Product with no stock
        self.set_product_amount(
            product=first_line.product_id,
            location=first_line.origin_location_id,
            amount=0,
        )
        self.assertEqual(first_line._get_available_quantity(), (0, 0))

        # Check Line without product
        second_line = wizard.stock_move_location_line_ids[1]
        second_line.product_id = False
        self.assertEqual(second_line._get_available_quantity(), (0, 0))
