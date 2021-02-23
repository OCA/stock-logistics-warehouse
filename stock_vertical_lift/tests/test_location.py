# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions

from .common import VerticalLiftCase


class TestVerticalLiftLocation(VerticalLiftCase):
    def test_vertical_lift_kind(self):
        # this boolean is what defines a "Vertical Lift View", the upper level
        # of the tree (View -> Shuttles -> Trays -> Cells)
        self.assertTrue(self.vertical_lift_loc.vertical_lift_location)
        self.assertEqual(self.vertical_lift_loc.vertical_lift_kind, "view")

        # check types accross the hierarchy
        shuttles = self.vertical_lift_loc.child_ids
        self.assertTrue(
            all(location.vertical_lift_kind == "shuttle" for location in shuttles)
        )
        trays = shuttles.mapped("child_ids")
        self.assertTrue(
            all(location.vertical_lift_kind == "tray" for location in trays)
        )
        cells = trays.mapped("child_ids")
        self.assertTrue(
            all(location.vertical_lift_kind == "cell" for location in cells)
        )

    def test_fetch_vertical_lift_tray(self):
        shuttles = self.vertical_lift_loc.child_ids
        trays = shuttles.mapped("child_ids")
        cells = trays.mapped("child_ids")
        self.assertTrue(cells[0].button_fetch_vertical_lift_tray())
        message = "cell_location cannot be set when the location is a cell."
        with self.assertRaisesRegex(ValueError, message):
            cells[0].fetch_vertical_lift_tray(cells[0])
        message = "Cannot fetch a vertical lift tray on location"
        with self.assertRaisesRegex(exceptions.UserError, message):
            shuttles[0].fetch_vertical_lift_tray(cells[0])
        self.assertTrue(cells[0].button_release_vertical_lift_tray())

    def test_create_shuttle(self):
        # any location created directly under the view is a shuttle
        shuttle_loc = self.env["stock.location"].create(
            {
                "name": "Shuttle 42",
                "location_id": self.vertical_lift_loc.id,
                "usage": "internal",
            }
        )
        self.assertEqual(shuttle_loc.vertical_lift_kind, "shuttle")
