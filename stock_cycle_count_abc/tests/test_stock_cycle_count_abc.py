# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo.addons.stock_cycle_count.tests import test_stock_cycle_count


class TestStockCycleCountAbc(test_stock_cycle_count.TestStockCycleCount):
    def setUp(self):
        super(TestStockCycleCountAbc, self).setUp()

        self.rule_abc = self._create_stock_cycle_count_rule_abc(
            self.manager, "ABC rule", "warehouse"
        )
        self.count_loc_cust = self.stock_location_model.create(
            {"name": "Place 1", "usage": "production"}
        )
        self.rule_abc2 = self._create_stock_cycle_count_rule_abc(
            self.manager, "ABC rule 2", "location", [self.count_loc_cust.id]
        )
        self.rule_ids = [
            self.rule_abc.id,
            self.rule_abc2.id,
        ]
        self.grp_a = self.env["stock.abc"].search([("name", "=", "A")])
        self.grp_b = self.env["stock.abc"].search([("name", "=", "B")])
        self.grp_c = self.env["stock.abc"].search([("name", "=", "C")])
        self.grp_a_products = self.env["product.template"].search([], limit=400)
        self.grp_b_products = self.env["product.template"].search([], limit=200)
        self.grp_c_products = self.env["product.template"].search([], limit=100)
        self.grp_a_products.write({"abc_id": self.grp_a.id})
        self.grp_b_products.write({"abc_id": self.grp_b.id})
        self.grp_c_products.write({"abc_id": self.grp_c.id})
        self.abc_wh = self.stock_warehouse_model.create(
            {
                "name": "ABC WH",
                "code": "c",
                "cycle_count_planning_horizon": 30,
                "counts_for_accuracy_qty": 1,
            }
        )
        self.abc_wh.write({"cycle_count_rule_ids": [(6, 0, self.rule_ids)]})

    def _create_stock_cycle_count_rule_abc(
        self, uid, name, apply_in, location_ids=False
    ):
        rule = self.stock_cycle_count_rule_model.with_user(uid).create(
            {
                "name": name,
                "rule_type": "abc",
                "frequency": "weekly",
                "apply_in": apply_in,
                "location_ids": location_ids,
            }
        )
        return rule

    def test_cycle_count_abc(self):
        wh = self.abc_wh
        locs = self.stock_location_model
        for rule in wh.cycle_count_rule_ids:
            locs += wh._search_cycle_count_locations(rule)
        locs = locs.exists()  # remove duplicated locations.
        loc = locs.filtered(lambda l: l.usage != "view")[0]
        date = datetime.today() - timedelta(days=1)
        wh.cron_cycle_count()
        cycle_counts = self.cycle_count_model.search(
            [("cycle_count_rule_id.rule_type", "=", "abc")]
        )
        self.inventory_model.create(
            {
                "name": "Pre-existing inventory",
                "location_ids": [(4, loc.id)],
                "date": date,
            }
        )
        for cc in cycle_counts.filtered(lambda c: c.state == "draft"):
            cc.action_create_inventory_adjustment()
            self.inventory_model.search([("cycle_count_id", "=", cc.id)])
            cc.sudo().action_view_inventory()
            cc.state = "done"
        wh.cron_cycle_count()
        cycle_counts[0].cycle_count_rule_id.frequency = "daily"
        wh.cron_cycle_count()
        cycle_counts[0].cycle_count_rule_id.frequency = "monthly"
        wh.cron_cycle_count()
        cycle_counts[0].cycle_count_rule_id.frequency = "quarterly"
        wh.cron_cycle_count()
