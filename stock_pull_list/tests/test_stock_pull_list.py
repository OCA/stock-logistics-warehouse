# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

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
