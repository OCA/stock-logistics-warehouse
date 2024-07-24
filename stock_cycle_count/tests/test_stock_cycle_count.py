# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import common


class TestStockCycleCount(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockCycleCount, cls).setUpClass()
        cls.res_users_model = cls.env["res.users"]
        cls.cycle_count_model = cls.env["stock.cycle.count"]
        cls.stock_cycle_count_rule_model = cls.env["stock.cycle.count.rule"]
        cls.inventory_model = cls.env["stock.inventory"]
        cls.stock_location_model = cls.env["stock.location"]
        cls.stock_move_model = cls.env["stock.move"]
        cls.stock_warehouse_model = cls.env["stock.warehouse"]
        cls.product_model = cls.env["product.product"]
        cls.quant_model = cls.env["stock.quant"]
        cls.move_model = cls.env["stock.move"]

        cls.company = cls.env.ref("base.main_company")
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.g_stock_manager = cls.env.ref("stock.group_stock_manager")
        cls.g_stock_user = cls.env.ref("stock.group_stock_user")

        # Create users:
        cls.manager = cls._create_user("user_1", [cls.g_stock_manager], cls.company).id
        cls.user = cls._create_user("user_2", [cls.g_stock_user], cls.company).id

        # Create warehouses:
        cls.big_wh = cls.stock_warehouse_model.create(
            {"name": "BIG", "code": "B", "cycle_count_planning_horizon": 30}
        )
        cls.small_wh = cls.stock_warehouse_model.create({"name": "SMALL", "code": "S"})

        # Create rules:
        cls.rule_periodic = cls._create_stock_cycle_count_rule_periodic(
            cls.manager, "rule_1", [2, 7]
        )
        cls.rule_turnover = cls._create_stock_cycle_count_rule_turnover(
            cls.manager, "rule_2", [100]
        )
        cls.rule_accuracy = cls._create_stock_cycle_count_rule_accuracy(
            cls.manager, "rule_3", [5], cls.big_wh.view_location_id.ids
        )
        cls.zero_rule = cls._create_stock_cycle_count_rule_zero(cls.manager, "rule_4")

        # Configure warehouses:
        cls.rule_ids = [
            cls.rule_periodic.id,
            cls.rule_turnover.id,
            cls.rule_accuracy.id,
            cls.zero_rule.id,
        ]
        cls.big_wh.write({"cycle_count_rule_ids": [(6, 0, cls.rule_ids)]})

        # Create locations:
        cls.count_loc = cls.stock_location_model.create(
            {"name": "Place", "usage": "production"}
        )
        cls.count_loc_2 = cls.stock_location_model.create(
            {"name": "Place 2", "usage": "production"}
        )
        cls.stock_location_model._parent_store_compute()

        # Create a cycle count:
        cls.cycle_count_1 = cls.cycle_count_model.with_user(cls.manager).create(
            {
                "name": "Test cycle count",
                "cycle_count_rule_id": cls.rule_periodic.id,
                "location_id": cls.count_loc.id,
            }
        )

        # Create a product:
        cls.product1 = cls.product_model.create(
            {"name": "Test Product 1", "type": "product", "default_code": "PROD1"}
        )
        cls.product2 = cls.product_model.create(
            {"name": "Test Product 2", "type": "product", "default_code": "PROD2"}
        )

    @classmethod
    def _create_user(cls, login, groups, company):
        group_ids = [group.id for group in groups]
        user = cls.res_users_model.create(
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

    @classmethod
    def _create_stock_cycle_count_rule_periodic(cls, uid, name, values):
        rule = cls.stock_cycle_count_rule_model.with_user(uid).create(
            {
                "name": name,
                "rule_type": "periodic",
                "periodic_qty_per_period": values[0],
                "periodic_count_period": values[1],
            }
        )
        return rule

    @classmethod
    def _create_stock_cycle_count_rule_turnover(cls, uid, name, values):
        rule = cls.stock_cycle_count_rule_model.with_user(uid).create(
            {
                "name": name,
                "rule_type": "turnover",
                "turnover_inventory_value_threshold": values[0],
            }
        )
        return rule

    @classmethod
    def _create_stock_cycle_count_rule_accuracy(cls, uid, name, values, zone_ids):
        rule = cls.stock_cycle_count_rule_model.with_user(uid).create(
            {
                "name": name,
                "rule_type": "accuracy",
                "accuracy_threshold": values[0],
                "apply_in": "location",
                "location_ids": [(6, 0, zone_ids)],
            }
        )
        return rule

    @classmethod
    def _create_stock_cycle_count_rule_zero(cls, uid, name):
        rule = cls.stock_cycle_count_rule_model.with_user(uid).create(
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
                "automatic_deadline_date": date_pre_existing_cc,
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
        # Remove the pre_existing_count
        self.inventory_model.search(
            [("cycle_count_id", "=", pre_existing_count.id)], limit=1
        ).unlink()
        pre_existing_count.unlink()
        # Execute cron for first time
        wh.cron_cycle_count()
        # There are counts in state open(execution) and not in state draft
        open_counts = self.cycle_count_model.search(
            [("location_id", "in", locs.ids), ("state", "=", "open")]
        )
        self.assertTrue(open_counts, "Cycle counts in execution state")
        draft_counts = self.cycle_count_model.search(
            [("location_id", "in", locs.ids), ("state", "=", "draft")]
        )
        self.assertFalse(draft_counts, "No Cycle counts in draft state")
        # Execute the cron for second time
        wh.cron_cycle_count()
        # New cycle counts for same location created in draft state
        draft_counts = self.cycle_count_model.search(
            [("location_id", "in", locs.ids), ("state", "=", "draft")]
        )
        self.assertTrue(draft_counts, "No Cycle counts in draft state")
        # Inventory adjustment only started for cycle counts in open state
        self.assertTrue(open_counts.stock_adjustment_ids)
        self.assertFalse(draft_counts.stock_adjustment_ids)
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
        inventory.action_state_to_in_progress()
        inventory.action_state_to_done()
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
        self.cycle_count_1.action_view_inventory()
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

    def test_inventory_adjustment_accuracy(self):
        date = datetime.today() - timedelta(days=1)
        # Create location
        loc = self.stock_location_model.create(
            {"name": "Test Location", "usage": "internal"}
        )
        # Create stock quants for specific location
        quant1 = self.quant_model.create(
            {
                "product_id": self.product1.id,
                "location_id": loc.id,
                "quantity": 10.0,
            }
        )
        quant2 = self.quant_model.create(
            {
                "product_id": self.product2.id,
                "location_id": loc.id,
                "quantity": 15.0,
            }
        )
        # Create adjustments for specific location
        adjustment = self.inventory_model.create(
            {
                "name": "Pre-existing inventory",
                "location_ids": [(4, loc.id)],
                "date": date,
            }
        )
        # Start the adjustment
        adjustment.action_state_to_in_progress()
        # Check that there are stock quants for the specific location
        self.assertTrue(self.env["stock.quant"].search([("location_id", "=", loc.id)]))
        # Make the count of the stock
        quant1.update(
            {
                "inventory_quantity": 5,
            }
        )
        quant2.update(
            {
                "inventory_quantity": 10,
            }
        )
        # Apply the changes
        quant1._apply_inventory()
        quant2._apply_inventory()
        # Check that line_accuracy is calculated properly
        sml = self.env["stock.move.line"].search(
            [("location_id", "=", loc.id), ("product_id", "=", self.product1.id)]
        )
        self.assertEqual(sml.line_accuracy, 0.5)
        sml = self.env["stock.move.line"].search(
            [("location_id", "=", loc.id), ("product_id", "=", self.product2.id)]
        )
        self.assertEqual(sml.line_accuracy, 0.6667000000000001)
        # Set Inventory Adjustment to Done
        adjustment.action_state_to_done()
        # Check that accuracy is correctly calculated
        self.assertEqual(adjustment.inventory_accuracy, 60)

    def test_zero_inventory_adjustment_accuracy(self):
        date = datetime.today() - timedelta(days=1)
        # Create location
        loc = self.stock_location_model.create(
            {"name": "Test Location", "usage": "internal"}
        )
        # Create stock quants for specific location
        quant1 = self.quant_model.create(
            {
                "product_id": self.product1.id,
                "location_id": loc.id,
                "quantity": 0.0,
            }
        )
        quant2 = self.quant_model.create(
            {
                "product_id": self.product2.id,
                "location_id": loc.id,
                "quantity": 0.0,
            }
        )
        # Create adjustment for specific location
        adjustment = self.inventory_model.create(
            {
                "name": "Pre-existing inventory qty zero",
                "location_ids": [(4, loc.id)],
                "date": date,
            }
        )
        # Start the adjustment
        adjustment.action_state_to_in_progress()
        # Check that there are stock quants for the specific location
        self.assertTrue(self.env["stock.quant"].search([("location_id", "=", loc.id)]))
        # Make the count of the stock
        quant1.update(
            {
                "inventory_quantity": 5,
            }
        )
        quant2.update(
            {
                "inventory_quantity": 10,
            }
        )
        # Apply the changes
        quant1._apply_inventory()
        quant2._apply_inventory()
        # Check that line_accuracy is calculated properly
        sml = self.env["stock.move.line"].search(
            [("location_id", "=", loc.id), ("product_id", "=", self.product1.id)]
        )
        self.assertEqual(sml.line_accuracy, 0)
        # Set Inventory Adjustment to Done
        adjustment.action_state_to_done()
        # Check that accuracy is correctly calculated
        self.assertEqual(adjustment.inventory_accuracy, 0)
        # Check discrepancy over 100%
        adjustment_2 = self.inventory_model.create(
            {
                "name": "Adjustment 2",
                "location_ids": [(4, loc.id)],
                "date": date,
            }
        )
        adjustment_2.action_state_to_in_progress()
        quant1.update(
            {
                "inventory_quantity": 1500,
            }
        )
        quant1._apply_inventory()
        # Check that line_accuracy is calculated properly
        sml = self.env["stock.move.line"].search(
            [("location_id", "=", loc.id), ("product_id", "=", self.product1.id)]
        )
        # Check that line_accuracy is still 0
        self.assertEqual(sml.line_accuracy, 0)

    def test_auto_start_inventory_from_cycle_count(self):
        # Set the auto_start_inventory_from_cycle_count rule to True
        self.company.auto_start_inventory_from_cycle_count = True
        # Create Cycle Count 1 cont_loc_2
        cycle_count_1 = self.cycle_count_model.create(
            {
                "name": "Cycle Count 1",
                "cycle_count_rule_id": self.rule_periodic.id,
                "location_id": self.count_loc_2.id,
                "date_deadline": "2026-11-30",
                "manual_deadline_date": "2026-11-30",
            }
        )
        cycle_count_1.flush()
        # Confirm the Cycle Count
        cycle_count_1.action_create_inventory_adjustment()
        # Inventory adjustments change their state to in_progress
        self.assertEqual(cycle_count_1.stock_adjustment_ids.state, "in_progress")

    def test_prefill_counted_quantity(self):
        self.company.inventory_adjustment_counted_quantities = "counted"
        date = datetime.today() - timedelta(days=1)
        # Create locations
        loc_1 = self.stock_location_model.create(
            {"name": "Test Location 1", "usage": "internal"}
        )
        loc_2 = self.stock_location_model.create(
            {"name": "Test Location 2", "usage": "internal"}
        )
        # Create stock quants for different locations
        quant_1 = self.quant_model.create(
            {
                "product_id": self.product1.id,
                "location_id": loc_1.id,
                "quantity": 25,
            }
        )
        quant_2 = self.quant_model.create(
            {
                "product_id": self.product1.id,
                "location_id": loc_2.id,
                "quantity": 50,
            }
        )
        # Create adjustments for different locations
        adjustment_1 = self.inventory_model.create(
            {
                "name": "Adjustment Location 1",
                "location_ids": [(4, loc_1.id)],
                "date": date,
            }
        )
        adjustment_2 = self.inventory_model.create(
            {
                "name": "Adjustment Location 2",
                "location_ids": [(4, loc_2.id)],
                "date": date,
            }
        )
        # Start the adjustment 1 with prefill quantity as counted
        adjustment_1.action_state_to_in_progress()
        # Check that the inventory_quantity is 25
        self.assertEqual(quant_1.inventory_quantity, 25)
        # Change company prefill option to zero
        self.company.inventory_adjustment_counted_quantities = "zero"
        # Start the adjustment 2 with prefill quantity as zero
        adjustment_2.action_state_to_in_progress()
        # Check that the inventory_quantity is 0
        self.assertEqual(quant_2.inventory_quantity, 0.0)
