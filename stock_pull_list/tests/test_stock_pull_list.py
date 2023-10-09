# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError

from .common import TestPullListCommon


class TestStockPullList(TestPullListCommon):
    def test_01_default_options(self):
        self._generate_moves()
        wiz = self.wiz_obj.create({})
        wiz.action_prepare()
        lines = wiz.line_ids.filtered(lambda l: l.product_id == self.product_a)
        self.assertEqual(len(lines), 2)
        line_1 = lines.filtered(lambda l: l.date == self.yesterday.date())
        self.assertEqual(line_1.raw_demand_qty, 50)
        self.assertEqual(line_1.needed_qty, 50)
        self.assertEqual(line_1.stock_rule_id, self.transfer_rule)

        line_2 = lines.filtered(lambda l: l.date == self.date_3.date())
        self.assertEqual(line_2.raw_demand_qty, 70)
        self.assertEqual(line_2.needed_qty, 70)

    def test_02_consolidate(self):
        self._generate_moves()
        wiz = self.wiz_obj.create({"consolidate_by_product": True})
        wiz.action_prepare()
        line = wiz.line_ids.filtered(lambda l: l.product_id == self.product_a)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.date, self.today.date())
        expected = 50 + 70
        self.assertEqual(line.raw_demand_qty, expected)
        self.assertEqual(line.needed_qty, expected)

    def test_03_no_needed_qty(self):
        """Tests that no line is created in the wizard if there's no
        quantity needed."""
        quantity = 120.00
        self._update_product_qty(self.product_a, quantity)
        self._generate_moves()
        wiz = self.wiz_obj.create({"consolidate_by_product": True})
        wiz.action_prepare()
        line = wiz.line_ids.filtered(lambda l: l.product_id == self.product_a)
        self.assertEqual(len(line), 0)

    def test_04_server_action(self):
        """Tests work of generate pull list server action
        first without allow_pull_list_server_action flag,
        after this check Raise of UserError when 2 different locations"""
        self._generate_moves()
        picking = self.picking_obj.search(
            [("location_id", "=", self.warehouse.lot_stock_id.id)]
        )
        self.assertRaises(UserError, picking.action_create_pull_list)
        picking.picking_type_id.update({"allow_pull_list_server_action": True})
        picking.action_create_pull_list()
        wizard = self.env["stock.pull.list.wizard"].search([])
        lines = wizard.line_ids.filtered(lambda l: l.product_id == self.product_a)
        self.assertEqual(len(lines), 2)
        line_1 = lines.filtered(lambda l: l.date == self.yesterday.date())
        self.assertEqual(line_1.raw_demand_qty, 50)
        self.assertEqual(line_1.needed_qty, 50)
        self.assertEqual(line_1.stock_rule_id, self.transfer_rule)
        picking[0].update({"location_id": self.customer_loc.id})
        self.assertRaises(UserError, picking.action_create_pull_list)
