# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import common


class TestStockCycleCount(common.TransactionCase):
    def setUp(self):
        super(TestStockCycleCount, self).setUp()
        self.res_users_model = self.env["res.users"]
        self.cycle_count_model = self.env["stock.cycle.count"]
        self.stock_cycle_count_rule_model = self.env["stock.cycle.count.rule"]
        self.inventory_model = self.env["stock.inventory"]
        self.stock_location_model = self.env["stock.location"]
        self.stock_move_model = self.env["stock.move"]
        self.stock_warehouse_model = self.env["stock.warehouse"]
        self.product_model = self.env["product.product"]
        self.quant_model = self.env["stock.quant"]
        self.move_model = self.env["stock.move"]

        self.company = self.env.ref("base.main_company")
        self.partner = self.env.ref("base.res_partner_1")
        self.g_stock_manager = self.env.ref("stock.group_stock_manager")
        self.g_stock_user = self.env.ref("stock.group_stock_user")

        # Create users:
        self.manager = self._create_user(
            "user_1", [self.g_stock_manager], self.company
        ).id
        self.user = self._create_user("user_2", [self.g_stock_user], self.company).id

        # Create warehouses:
        self.big_wh = self.stock_warehouse_model.create(
            {"name": "BIG", "code": "B", "cycle_count_planning_horizon": 30}
        )
        self.small_wh = self.stock_warehouse_model.create(
            {"name": "SMALL", "code": "S"}
        )

        # Create rules:
        self.rule_periodic = self._create_stock_cycle_count_rule_periodic(
            self.manager, "rule_1", [2, 7]
        )
        self.rule_turnover = self._create_stock_cycle_count_rule_turnover(
            self.manager, "rule_2", [100]
        )
        self.rule_accuracy = self._create_stock_cycle_count_rule_accuracy(
            self.manager, "rule_3", [5], self.big_wh.view_location_id.ids
        )
        self.zero_rule = self._create_stock_cycle_count_rule_zero(
            self.manager, "rule_4"
        )

        # Configure warehouses:
        self.rule_ids = [
            self.rule_periodic.id,
            self.rule_turnover.id,
            self.rule_accuracy.id,
            self.zero_rule.id,
        ]
        self.big_wh.write({"cycle_count_rule_ids": [(6, 0, self.rule_ids)]})

        # Create a location:
        self.count_loc = self.stock_location_model.create(
            {"name": "Place", "usage": "production"}
        )
        self.stock_location_model._parent_store_compute()

        # Create a cycle count:
        self.cycle_count_1 = self.cycle_count_model.with_user(self.manager).create(
            {
                "name": "Test cycle count",
                "cycle_count_rule_id": self.rule_periodic.id,
                "location_id": self.count_loc.id,
            }
        )

        # Create a product:
        self.product1 = self.product_model.create(
            {"name": "Test Product 1", "type": "product", "default_code": "PROD1"}
        )

    def _create_user(self, login, groups, company):
        group_ids = [group.id for group in groups]
        user = self.res_users_model.create(
            {
                "name": login,
                "login": login,
                "email": "example@yourcompany.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "groups_id": [(6, 0, group_ids)],
            }
        )
        return user

    def _create_stock_cycle_count_rule_periodic(self, uid, name, values):
        rule = self.stock_cycle_count_rule_model.with_user(uid).create(
            {
                "name": name,
                "rule_type": "periodic",
                "periodic_qty_per_period": values[0],
                "periodic_count_period": values[1],
            }
        )
        return rule

    def _create_stock_cycle_count_rule_turnover(self, uid, name, values):
        rule = self.stock_cycle_count_rule_model.with_user(uid).create(
            {
                "name": name,
                "rule_type": "turnover",
                "turnover_inventory_value_threshold": values[0],
            }
        )
        return rule

    def _create_stock_cycle_count_rule_accuracy(self, uid, name, values, zone_ids):
        rule = self.stock_cycle_count_rule_model.with_user(uid).create(
            {
                "name": name,
                "rule_type": "accuracy",
                "accuracy_threshold": values[0],
                "apply_in": "location",
                "location_ids": [(6, 0, zone_ids)],
            }
        )
        return rule

    def _create_stock_cycle_count_rule_zero(self, uid, name):
        rule = self.stock_cycle_count_rule_model.with_user(uid).create(
            {"name": name, "rule_type": "zero"}
        )
        return rule

    def test_cycle_count_planner(self):
        """Tests creation of cycle counts."""
        # Common rules:
        wh = self.big_wh
        locs = self.stock_location_model
        for rule in self.big_wh.cycle_count_rule_ids:
            locs += wh._search_cycle_count_locations(rule)
        locs = locs.exists()  # remove duplicated locations.
        counts = self.cycle_count_model.search([("location_id", "in", locs.ids)])
        self.assertFalse(counts, "Existing cycle counts before execute planner.")
        date_pre_existing_cc = datetime.today() + timedelta(days=30)
        loc = locs.filtered(lambda l: l.usage != "view")[0]
        pre_existing_count = self.cycle_count_model.create(
            {
                "name": "To be cancelled when running cron job.",
                "cycle_count_rule_id": self.rule_periodic.id,
                "location_id": loc.id,
                "date_deadline": date_pre_existing_cc,
            }
        )
        self.assertEqual(
            pre_existing_count.state, "draft", "Testing data not generated properly."
        )
        date = datetime.today() - timedelta(days=1)
        self.inventory_model.create(
            {
                "name": "Pre-existing inventory",
                "location_ids": [(4, loc.id)],
                "date": date,
            }
        )
        self.quant_model.create(
            {
                "product_id": self.product1.id,
                "location_id": self.count_loc.id,
                "quantity": 1.0,
            }
        )
        move1 = self.stock_move_model.create(
            {
                "name": "Pre-existing move",
                "product_id": self.product1.id,
                "product_uom_qty": 1.0,
                "product_uom": self.product1.uom_id.id,
                "location_id": self.count_loc.id,
                "location_dest_id": loc.id,
            }
        )
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids[0].qty_done = 1.0
        move1._action_done()
        wh.cron_cycle_count()
        self.assertNotEqual(
            pre_existing_count.date_deadline,
            date_pre_existing_cc,
            "Date of pre-existing cycle counts has not been " "updated.",
        )
        counts = self.cycle_count_model.search([("location_id", "in", locs.ids)])
        self.assertTrue(counts, "Cycle counts not planned")
        # Zero-confirmations:
        count = self.cycle_count_model.search(
            [
                ("location_id", "=", loc.id),
                ("cycle_count_rule_id", "=", self.zero_rule.id),
            ]
        )
        self.assertFalse(count, "Unexpected zero confirmation.")
        move2 = self.move_model.create(
            {
                "name": "make the locations to run out of stock.",
                "product_id": self.product1.id,
                "product_uom_qty": 1.0,
                "product_uom": self.product1.uom_id.id,
                "location_id": loc.id,
                "location_dest_id": self.count_loc.id,
            }
        )
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids[0].qty_done = 1.0
        move2._action_done()
        count = self.cycle_count_model.search(
            [
                ("location_id", "=", loc.id),
                ("cycle_count_rule_id", "=", self.zero_rule.id),
            ]
        )
        self.assertTrue(count, "Zero confirmation not being created.")

    def test_cycle_count_workflow(self):
        """Tests workflow."""
        self.cycle_count_1.action_create_inventory_adjustment()
        inventory = self.inventory_model.search(
            [("cycle_count_id", "=", self.cycle_count_1.id)]
        )
        self.assertTrue(inventory, "Inventory not created.")
        inventory.action_start()
        inventory.action_validate()
        self.assertEqual(
            self.cycle_count_1.state, "done", "Cycle count not set as done."
        )
        self.cycle_count_1.do_cancel()
        self.assertEqual(
            self.cycle_count_1.state, "cancelled", "Cycle count not set as cancelled."
        )

    def test_view_methods(self):
        """Tests the methods used to handle views."""
        self.cycle_count_1.action_create_inventory_adjustment()
        self.cycle_count_1.sudo().action_view_inventory()
        inv_count = self.cycle_count_1.inventory_adj_count
        self.assertEqual(inv_count, 1, "View method failing.")
        rules = [
            self.rule_periodic,
            self.rule_turnover,
            self.rule_accuracy,
            self.zero_rule,
        ]
        for r in rules:
            r._compute_rule_description()
            self.assertTrue(r.rule_description, "No description provided")
        self.rule_accuracy._onchange_locaton_ids()
        self.assertEqual(
            self.rule_accuracy.warehouse_ids.ids,
            self.big_wh.ids,
            "Rules defined for zones are not getting the right " "warehouse.",
        )

    def test_user_security(self):
        """Tests user rights."""
        with self.assertRaises(AccessError):
            self._create_stock_cycle_count_rule_periodic(self.user, "rule_1b", [2, 7])
        with self.assertRaises(AccessError):
            self.cycle_count_1.with_user(self.user).unlink()

    def test_rule_periodic_constrains(self):
        """Tests the constrains for the periodic rules."""
        # constrain: periodic_qty_per_period < 1
        with self.assertRaises(ValidationError):
            self._create_stock_cycle_count_rule_periodic(self.manager, "rule_0", [0, 0])
        # constrain: periodic_count_period < 0
        with self.assertRaises(ValidationError):
            self._create_stock_cycle_count_rule_periodic(
                self.manager, "rule_0", [1, -1]
            )

    def test_rule_zero_constrains(self):
        """Tests the constrains for the zero-confirmation rule: it might
        only exist one zero confirmation rule per warehouse and have just
        one warehouse assigned.
        """
        zero2 = self._create_stock_cycle_count_rule_zero(self.manager, "zero_rule_2")
        with self.assertRaises(ValidationError):
            zero2.warehouse_ids = [(4, self.big_wh.id)]
        with self.assertRaises(ValidationError):
            self.zero_rule.warehouse_ids = [(4, self.small_wh.id)]

    def test_auto_link_inventory_to_cycle_count_1(self):
        """Create an inventory that could fit a planned cycle count should
        auto-link it to that cycle count."""
        self.assertEqual(self.cycle_count_1.state, "draft")
        inventory = self.inventory_model.create(
            {
                "name": "new inventory",
                "location_ids": [(4, self.count_loc.id)],
                "exclude_sublocation": True,
            }
        )
        self.assertEqual(inventory.cycle_count_id, self.cycle_count_1)
        self.assertEqual(self.cycle_count_1.state, "open")

    def test_auto_link_inventory_to_cycle_count_2(self):
        """Test auto-link when exclude sublocation is no set."""
        self.assertEqual(self.cycle_count_1.state, "draft")
        inventory = self.inventory_model.create(
            {"name": "new inventory", "location_ids": [(4, self.count_loc.id)]}
        )
        self.assertEqual(inventory.cycle_count_id, self.cycle_count_1)
        self.assertEqual(self.cycle_count_1.state, "open")

    def test_cycle_count_contrains(self):
        """Test the various constrains defined in the inventory adjustment."""
        self.cycle_count_1.action_create_inventory_adjustment()
        inventory = self.inventory_model.search(
            [("cycle_count_id", "=", self.cycle_count_1.id)]
        )
        with self.assertRaises(ValidationError):
            inventory.product_ids = self.product1
        with self.assertRaises(ValidationError):
            inventory.location_ids = False
        loc = self.stock_location_model.create(
            {"name": "Second Location", "usage": "internal"}
        )
        with self.assertRaises(ValidationError):
            inventory.location_ids += loc
        with self.assertRaises(ValidationError):
            inventory.exclude_sublocation = False
        company = self.env["res.company"].create({"name": "Test"})
        with self.assertRaises(ValidationError):
            inventory.company_id = company
