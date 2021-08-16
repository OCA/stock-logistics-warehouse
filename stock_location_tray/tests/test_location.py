# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions

from .common import LocationTrayTypeCase


class TestLocation(LocationTrayTypeCase):
    def test_create_tray(self):
        tray_type = self.tray_type_small_8x
        tray_loc = self._create_tray_z(tray_type)

        self.assertEqual(len(tray_loc.child_ids), tray_type.cols * tray_type.rows)  # 8
        self.assertTrue(
            all(
                subloc.cell_in_tray_type_id == tray_type
                for subloc in tray_loc.child_ids
            )
        )

    def test_tray_has_stock(self):
        cell = self.env.ref("stock_location_tray.stock_location_tray_demo_x3y2")
        self.assertFalse(cell.quant_ids)
        self.assertFalse(cell.tray_cell_contains_stock)
        self._update_quantity_in_cell(cell, self.product, 1)
        self.assertTrue(cell.quant_ids)
        self.assertTrue(cell.tray_cell_contains_stock)
        self._update_quantity_in_cell(cell, self.product, -1)
        self.assertTrue(cell.quant_ids)
        self.assertFalse(cell.tray_cell_contains_stock)

    def test_matrix_empty_tray(self):
        self.assertEqual(self.tray_location.tray_type_id.cols, 4)
        self.assertEqual(self.tray_location.tray_type_id.rows, 2)
        self.assertEqual(
            self.tray_location.tray_matrix,
            {
                # we show the entire tray, not a cell
                "selected": [],
                # we have no stock in this location
                # fmt: off
                'cells': [
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                ]
                # fmt: on
            },
        )
        saved_tray_type = self.tray_location.tray_type_id
        self.tray_location.tray_type_id = False
        self.assertEqual(self.tray_location.tray_matrix, {})
        subloc = self.tray_location.create({"name": "Sub Location"})
        self.tray_location.write({"child_ids": [(6, 0, subloc.id)]})
        message = "Location %s has sub-locations, it cannot be converted to a tray."
        with self.assertRaisesRegex(
            exceptions.UserError, message % (self.tray_location.display_name)
        ):
            self.tray_location.tray_type_id = saved_tray_type

    def test_matrix_stock_tray(self):
        self._update_quantity_in_cell(
            self._cell_for(self.tray_location, x=1, y=1), self.product, 100
        )
        self._update_quantity_in_cell(
            self._cell_for(self.tray_location, x=2, y=1), self.product, 100
        )
        self._update_quantity_in_cell(
            self._cell_for(self.tray_location, x=4, y=2), self.product, 100
        )
        self.assertEqual(self.tray_location.tray_type_id.cols, 4)
        self.assertEqual(self.tray_location.tray_type_id.rows, 2)
        self.assertEqual(
            self.tray_location.tray_matrix,
            {
                # We show the entire tray, not a cell.
                "selected": [],
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

    def test_action_tray_matrix_click(self):
        location_view = self.tray_location.action_tray_matrix_click(2, 1)
        self.assertEqual(location_view["res_model"], "stock.location")
        cell = self.env.ref("stock_location_tray.stock_location_tray_demo_x3y2")
        location_view = cell.action_tray_matrix_click(2, 1)
        self.assertEqual(location_view["res_model"], "stock.location")

    def test_matrix_stock_cell(self):
        self.tray_location.tray_type_id = self.env.ref(
            "stock_location_tray.stock_location_tray_type_large_32x"
        )
        cell = self._cell_for(self.tray_location, x=7, y=3)
        self._update_quantity_in_cell(cell, self.product, 100)
        self._update_quantity_in_cell(
            self._cell_for(self.tray_location, x=1, y=1), self.product, 100
        )
        self._update_quantity_in_cell(
            self._cell_for(self.tray_location, x=3, y=2), self.product, 100
        )
        self.assertEqual(self.tray_location.tray_type_id.cols, 8)
        self.assertEqual(self.tray_location.tray_type_id.rows, 4)
        self.assertEqual(
            cell.tray_matrix,
            {
                # When called on a cell, we expect to have its coords. Worth to
                # note: the cell's coordinate are 7 and 3 in the posx and posy
                # fields as they make sense for humans. Here, they are offset
                # by -1 to have the indexes in the matrix.
                "selected": [6, 2],
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
        cell = self.env.ref("stock_location_tray.stock_location_tray_demo_x3y2")
        self.assertFalse(cell.tray_cell_contains_stock)
        # allowed to archive empty cell
        cell.active = False

    def test_check_active_not_empty(self):
        cell = self.env.ref("stock_location_tray.stock_location_tray_demo_x3y2")
        self._update_quantity_in_cell(cell, self.product, 1)
        self.assertTrue(cell.tray_cell_contains_stock)

        # we cannot archive an empty cell or any parent
        location = cell
        message = "You still have some product in locations"
        while location:
            with self.assertRaisesRegex(exceptions.UserError, message):
                location.active = False

            # restore state for the next test loop
            location.active = True
            location = location.location_id
            if location == self.wh.lot_stock_id:
                # we can't disable the Stock location anyway
                break

    def test_change_tray_type_when_empty(self):
        tray_type = self.tray_type_small_32x
        self.tray_location.tray_type_id = tray_type
        self.assertEqual(
            len(self.tray_location.child_ids), tray_type.cols * tray_type.rows  # 32
        )

    def test_change_tray_type_error_when_not_empty(self):
        self._update_quantity_in_cell(
            self._cell_for(self.tray_location, x=1, y=1), self.product, 1
        )
        tray_type = self.tray_type_small_32x
        message = "You still have some product in locations"
        with self.assertRaisesRegex(exceptions.UserError, message):
            self.tray_location.tray_type_id = tray_type

    def test_location_center_pos(self):
        cell = self.env.ref("stock_location_tray.stock_location_tray_demo_x3y2")
        tray_type = cell.cell_in_tray_type_id
        number_of_x = 4
        number_of_y = 2
        self.assertEqual((number_of_x, number_of_y), (tray_type.cols, tray_type.rows))

        total_width = 80
        total_depth = 30
        tray_type.width = total_width
        tray_type.depth = total_depth

        self.assertEqual(
            (total_width / number_of_x, total_depth / number_of_y),
            (tray_type.width_per_cell, tray_type.depth_per_cell),
        )
        from_left, from_bottom = cell.tray_cell_center_position()
        # fmt: off
        expected_left = (
            (total_width / number_of_x)  # width of a cell
            * 2  # we want the center of the cell x3, so we want 2 full cells
            + ((total_width / number_of_x) / 2)  # + the half of our cell
        )
        expected_bottom = (
            (total_depth / number_of_y)  # depth of a cell
            * 1  # we want the center of the cell y2, so we want 1 full cells
            + ((total_depth / number_of_y) / 2)  # + the half of our cell
        )
        # fmt: on
        self.assertEqual(from_left, expected_left)
        self.assertEqual(from_bottom, expected_bottom)

        self.assertEqual(self.tray_location.tray_cell_center_position(), (0, 0))

    def test_cell_name_format_posz(self):
        location = self.tray_location
        location.cell_name_format = "x{x:0>2}, y{y:0>2}"
        self.assertEqual(location.child_ids[0].name, "x01, y01")
        location.posz = 1
        self.assertEqual(location.mapped("posz"), [1])
        self.assertEqual(
            location.child_ids.mapped("posz"), [1] * len(location.child_ids)
        )

    def test_create_tray_xmlids(self):
        module = "stock_location_tray"
        tray_z = self._create_tray_z()
        # Cover if not location.cell_in_tray_type_id
        tray_z._create_tray_xmlids(module)
        # Cover if not tray_external_id
        tray_z.child_ids._create_tray_xmlids(module)
        values = {
            "name": "stock_location_tray_z",
            "module": module,
            "model": tray_z._name,
            "res_id": tray_z.id,
            "noupdate": 1,
        }
        self.env["ir.model.data"].create(values)
        # Cover if module != namespace
        tray_z.child_ids._create_tray_xmlids("no_module")
        tray_z.child_ids._create_tray_xmlids(module)
