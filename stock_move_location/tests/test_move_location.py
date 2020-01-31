# Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from .test_common import TestsCommon
from odoo.exceptions import ValidationError


class TestMoveLocation(TestsCommon):

    def setUp(self):
        super().setUp()
        self.setup_product_amounts()

    def _create_wizard(self, origin_location, destination_location):
        return self.wizard_obj.create({
            "origin_location_id": origin_location.id,
            "destination_location_id": destination_location.id,
        })

    def test_move_location_wizard(self):
        """Test a simple move."""
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.onchange_origin_location()
        wizard.action_move_location()
        self.check_product_amount(
            self.product_no_lots, self.internal_loc_1, 0,
        )
        self.check_product_amount(
            self.product_lots, self.internal_loc_1, 0, self.lot1,
        )
        self.check_product_amount(
            self.product_lots, self.internal_loc_1, 0, self.lot2,
        )
        self.check_product_amount(
            self.product_lots, self.internal_loc_1, 0, self.lot3,
        )
        self.check_product_amount(
            self.product_no_lots, self.internal_loc_2, 123,
        )
        self.check_product_amount(
            self.product_lots, self.internal_loc_2, 1, self.lot1,
        )
        self.check_product_amount(
            self.product_lots, self.internal_loc_2, 1, self.lot2,
        )
        self.check_product_amount(
            self.product_lots, self.internal_loc_2, 1, self.lot3,
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
            self.product_no_lots,
            self.internal_loc_1,
            50,
        )
        self.quant_obj._update_reserved_quantity(
            self.product_lots,
            self.internal_loc_1,
            1,
            lot_id=self.lot1,
        )
        # doesn't care about reservations, everything is moved
        wizard.action_move_location()
        self.check_product_amount(
            self.product_no_lots, self.internal_loc_1, 0,
        )
        self.check_product_amount(
            self.product_no_lots, self.internal_loc_2, 123,
        )
        self.check_product_amount(
            self.product_lots, self.internal_loc_2, 1, self.lot1,
        )

    def test_wizard_clear_lines(self):
        """Test lines getting cleared properly."""
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.onchange_origin_location()
        self.assertEqual(len(wizard.stock_move_location_line_ids), 4)
        wizard._onchange_destination_location_id()
        self.assertEqual(len(wizard.stock_move_location_line_ids), 4)
        dest_location_line = wizard.stock_move_location_line_ids.mapped(
            'destination_location_id')
        self.assertEqual(dest_location_line, wizard.destination_location_id)
        wizard._onchange_origin_location_id()
        self.assertEqual(len(wizard.stock_move_location_line_ids), 0)

    def test_planned_transfer(self):
        """Test planned transfer."""
        wizard = self._create_wizard(self.internal_loc_1, self.internal_loc_2)
        wizard.onchange_origin_location()
        wizard = wizard.with_context({'planned': True})
        wizard.action_move_location()
        picking = wizard.picking_id
        self.assertEqual(picking.state, 'assigned')
        self.assertEqual(len(picking.move_line_ids), 4)
        self.assertEqual(
            sorted(picking.move_line_ids.mapped("product_uom_qty")),
            [1, 1, 1, 123],
        )

    def test_quant_transfer(self):
        """Test quants transfer."""
        quants = self.product_lots.stock_quant_ids
        wizard = self.wizard_obj.with_context(
            active_model='stock.quant',
            active_ids=quants.ids,
            origin_location_disable=True
        ).create({
            "origin_location_id": quants[:1].location_id.id,
            "destination_location_id": self.internal_loc_2.id,
        })
        lines = wizard.stock_move_location_line_ids
        self.assertEqual(len(lines), 3)
        wizard.onchange_origin_location()
        self.assertEqual(len(lines), 3)
        wizard.destination_location_id = self.internal_loc_1
        wizard._onchange_destination_location_id()
        self.assertEqual(
            lines.mapped('destination_location_id'), self.internal_loc_1)
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
