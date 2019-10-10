# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import unittest

from .common import VerticalLiftCase


class TestInventory(VerticalLiftCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_out = cls.env.ref(
            "stock_vertical_lift.stock_picking_out_demo_vertical_lift_1"
        )
        # we have a move line to pick created by demo picking
        # stock_picking_out_demo_vertical_lift_1
        cls.out_move_line = cls.picking_out.move_line_ids

    def test_switch_inventory(self):
        self.shuttle.switch_inventory()
        self.assertEqual(self.shuttle.mode, "inventory")

    @unittest.skip("Not implemented")
    def test_inventory_count_move_lines(self):
        pass

    @unittest.skip("Not implemented")
    def test_process_current_inventory(self):
        # test to implement when the code is implemented
        self.shuttle.switch_inventory()
