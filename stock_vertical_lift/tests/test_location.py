# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions

from .common import VerticalLiftCase


class TestVerticalLiftLocation(VerticalLiftCase):
    def test_vertical_lift_kind(self):
        # this boolean is what defines a "Vertical Lift View", the upper level
        # of the tree (View -> Shuttles -> Trays -> Cells)
        self.assertTrue(self.vertical_lift_loc.vertical_lift_location)
        self.assertEqual(self.vertical_lift_loc.vertical_lift_kind, 'view')

        # check types accross the hierarchy
        shuttles = self.vertical_lift_loc.child_ids
        self.assertTrue(
            all(
                location.vertical_lift_kind == 'shuttle'
                for location in shuttles
            )
        )
        trays = shuttles.mapped('child_ids')
        self.assertTrue(
            all(location.vertical_lift_kind == 'tray' for location in trays)
        )
        cells = trays.mapped('child_ids')
        self.assertTrue(
            all(location.vertical_lift_kind == 'cell' for location in cells)
        )

    def test_create_shuttle(self):
        # any location created directly under the view is a shuttle
        shuttle_loc = self.env['stock.location'].create(
            {
                'name': 'Shuttle 42',
                'location_id': self.vertical_lift_loc.id,
                'usage': 'internal',
            }
        )
        self.assertEqual(shuttle_loc.vertical_lift_kind, 'shuttle')

    def test_create_tray(self):
        # any location created directly under a shuttle is a tray
        shuttle_loc = self.env.ref(
            'stock_vertical_lift.stock_location_vertical_lift_demo_shuttle_1'
        )
        tray_type = self.tray_type_small_8x
        tray_loc = self.env['stock.location'].create(
            {
                'name': 'Tray Z',
                'location_id': shuttle_loc.id,
                'usage': 'internal',
                'vertical_lift_tray_type_id': tray_type.id,
            }
        )

        self.assertEqual(tray_loc.vertical_lift_kind, 'tray')
        self.assertEqual(
            len(tray_loc.child_ids), tray_type.cols * tray_type.rows  # 8
        )

    def test_tray_has_stock(self):
        cell = self.env.ref(
            'stock_vertical_lift.stock_location_vertical_lift_demo_tray_1a_x3y2'
        )
        self.assertFalse(cell.quant_ids)
        self.assertFalse(cell.tray_cell_contains_stock)
        self._update_quantity_in_cell(cell, self.product_socks, 1)
        self.assertTrue(cell.quant_ids)
        self.assertTrue(cell.tray_cell_contains_stock)
        self._update_quantity_in_cell(cell, self.product_socks, -1)
        self.assertTrue(cell.quant_ids)
        self.assertFalse(cell.tray_cell_contains_stock)

    def test_matrix_empty_tray(self):
        tray_loc = self.env.ref(
            'stock_vertical_lift.stock_location_vertical_lift_demo_tray_1a'
        )
        self.assertEqual(tray_loc.vertical_lift_tray_type_id.cols, 4)
        self.assertEqual(tray_loc.vertical_lift_tray_type_id.rows, 2)
        self.assertEqual(
            tray_loc.tray_matrix,
            {
                # we show the entire tray, not a cell
                'selected': [],
                # we have no stock in this location
                # fmt: off
                'cells': [
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                ]
                # fmt: on
            },
        )

    def test_matrix_stock_tray(self):
        tray_loc = self.env.ref(
            'stock_vertical_lift.stock_location_vertical_lift_demo_tray_1a'
        )
        self._update_quantity_in_cell(
            self._cell_for(tray_loc, x=1, y=1), self.product_socks, 100
        )
        self._update_quantity_in_cell(
            self._cell_for(tray_loc, x=2, y=1), self.product_socks, 100
        )
        self._update_quantity_in_cell(
            self._cell_for(tray_loc, x=4, y=2), self.product_socks, 100
        )
        self.assertEqual(tray_loc.vertical_lift_tray_type_id.cols, 4)
        self.assertEqual(tray_loc.vertical_lift_tray_type_id.rows, 2)
        self.assertEqual(
            tray_loc.tray_matrix,
            {
                # We show the entire tray, not a cell.
                'selected': [],
                # Note: the coords are stored according to their index in the
                # arrays so it is easier to manipulate them. However, we
                # display them with the Y axis inverted in the UI to represent
                # the view of the operator.
                #
                #   [0, 0, 0, 1],
                #   [1, 1, 0, 0],
                #
                # fmt: off
                'cells': [
                    [1, 1, 0, 0],
                    [0, 0, 0, 1],
                ]
                # fmt: on
            },
        )

    def test_matrix_stock_cell(self):
        tray_loc = self.env.ref(
            'stock_vertical_lift.stock_location_vertical_lift_demo_tray_1c'
        )
        cell = self._cell_for(tray_loc, x=7, y=3)
        self._update_quantity_in_cell(cell, self.product_socks, 100)
        self._update_quantity_in_cell(
            self._cell_for(tray_loc, x=1, y=1), self.product_socks, 100
        )
        self._update_quantity_in_cell(
            self._cell_for(tray_loc, x=3, y=2), self.product_socks, 100
        )
        self.assertEqual(tray_loc.vertical_lift_tray_type_id.cols, 8)
        self.assertEqual(tray_loc.vertical_lift_tray_type_id.rows, 4)
        self.assertEqual(
            cell.tray_matrix,
            {
                # When called on a cell, we expect to have its coords. Worth to
                # note: the cell's coordinate are 7 and 3 in the posx and posy
                # fields as they make sense for humans. Here, they are offset
                # by -1 to have the indexes in the matrix.
                'selected': [6, 2],
                # fmt: off
                'cells': [
                    [1, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                ]
                # fmt: on
            },
        )

    def test_check_active_empty(self):
        # this type used by tray T1B, we should not be able to disable it
        cell = self.env.ref(
            'stock_vertical_lift.stock_location_vertical_lift_demo_tray_1a_x3y2'
        )
        self.assertFalse(cell.tray_cell_contains_stock)
        # allowed to archive empty cell
        cell.active = False

    def test_check_active_not_empty(self):
        cell = self.env.ref(
            'stock_vertical_lift.stock_location_vertical_lift_demo_tray_1a_x3y2'
        )
        self._update_quantity_in_cell(cell, self.product_socks, 1)
        self.assertTrue(cell.tray_cell_contains_stock)

        # we cannot archive an empty cell or any parent
        location = cell
        message = 'cannot be archived'
        while location:
            with self.assertRaisesRegex(exceptions.ValidationError, message):
                location.active = False

            # restore state for the next test loop
            location.active = True
            parent = location.location_id
            location = parent if parent.vertical_lift_kind else None

    def test_change_tray_type_when_empty(self):
        tray = self.env.ref(
            'stock_vertical_lift.stock_location_vertical_lift_demo_tray_1a'
        )
        tray_type = self.tray_type_small_32x
        tray.vertical_lift_tray_type_id = tray_type
        self.assertEqual(
            len(tray.child_ids), tray_type.cols * tray_type.rows  # 32
        )

    def test_change_tray_type_error_when_not_empty(self):
        tray = self.env.ref(
            'stock_vertical_lift.stock_location_vertical_lift_demo_tray_1a'
        )
        self._update_quantity_in_cell(
            self._cell_for(tray, x=1, y=1), self.product_socks, 1
        )
        tray_type = self.tray_type_small_32x
        message = 'cannot be modified when they contain products'
        with self.assertRaisesRegex(exceptions.UserError, message):
            tray.vertical_lift_tray_type_id = tray_type
