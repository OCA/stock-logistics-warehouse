# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
