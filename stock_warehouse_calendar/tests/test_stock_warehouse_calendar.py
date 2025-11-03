# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from freezegun import freeze_time

from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestStockWarehouseCalendar(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh_obj = cls.env["stock.warehouse"]
        cls.move_obj = cls.env["stock.move"]
        cls.picking_obj = cls.env["stock.picking"]
        cls.rule_obj = cls.env["stock.rule"]

        cls.company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.company_partner = cls.env.ref("base.main_partner")
        cls.calendar = cls.env.ref("resource.resource_calendar_std")
        cls.warehouse.calendar_id = cls.calendar
        cls.warehouse_2 = cls.wh_obj.create(
            {"code": "WH-T", "name": "Warehouse Test", "calendar_id": cls.calendar.id}
        )
        cls.warehouse_3 = cls.wh_obj.create(
            {"code": "WH-no-calendar", "name": "Warehouse Test 2"}
        )

        cls.wh2_bin_loc = cls.env["stock.location"].create(
            {
                "name": "Test Dest",
                "usage": "internal",
                "location_id": cls.warehouse_2.view_location_id.id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {"name": "test product", "default_code": "PRD", "is_storable": True}
        )

        # Create transfer route and rule
        route_vals = {"name": "WH-T -> WH"}
        cls.transfer_route = cls.env["stock.route"].create(route_vals)
        rule_vals = {
            "location_dest_id": cls.warehouse.lot_stock_id.id,
            "location_src_id": cls.warehouse_2.lot_stock_id.id,
            "action": "pull",
            "warehouse_id": cls.warehouse.id,
            "picking_type_id": cls.env.ref("stock.picking_type_internal").id,
            "name": "WH-T->WH",
            "route_id": cls.transfer_route.id,
            "delay": 1,
        }
        cls.transfer_rule = cls.rule_obj.create(rule_vals)

        # Create push route and rule with calendar
        cls.push_route = cls.env["stock.route"].create(
            {
                "name": "Push Route",
                "warehouse_selectable": True,
            }
        )
        cls.push_rule = cls.rule_obj.create(
            {
                "name": "Push with calendar",
                "action": "push",
                "picking_type_id": cls.env.ref("stock.picking_type_internal").id,
                "location_src_id": cls.warehouse_2.lot_stock_id.id,
                "location_dest_id": cls.wh2_bin_loc.id,
                "warehouse_id": cls.warehouse_2.id,
                "route_id": cls.push_route.id,
                "delay": 1,  # 1 day delay
            }
        )

        # Create push rule without calendar
        cls.push_rule_no_calendar = cls.rule_obj.create(
            {
                "name": "Push without calendar",
                "action": "push",
                "picking_type_id": cls.env.ref("stock.picking_type_internal").id,
                "location_src_id": cls.warehouse_3.lot_stock_id.id,
                "location_dest_id": cls.warehouse.lot_stock_id.id,
                "warehouse_id": cls.warehouse_3.id,  # Warehouse with no calendar
                "route_id": cls.push_route.id,
                "delay": 1,  # 1 day delay
            }
        )

        cls.product.route_ids = [(6, 0, [cls.push_route.id, cls.transfer_route.id])]

    def test_01_procurement_with_calendar(self):
        """Ensure procurement respects the company's working calendar
        when calculating the planned stock move date."""
        values = {
            "date_planned": "2097-01-07 09:00:00",  # Monday inside working hours
            "warehouse_id": self.warehouse,
            "company_id": self.company,
            "rule_id": self.transfer_rule,
        }
        self.rule_obj.run(
            [
                self.rule_obj.Procurement(
                    self.product,
                    100,
                    self.product.uom_id,
                    self.warehouse.lot_stock_id,
                    "Test",
                    "Test",
                    self.warehouse.company_id,
                    values,
                )
            ]
        )
        move = self.move_obj.search([("product_id", "=", self.product.id)], limit=1)
        date = fields.Date.to_date(move.date)
        # Friday 4th Jan 2097
        friday = fields.Date.to_date("2097-01-04 09:00:00")

        self.assertEqual(date, friday)

    def test_02_procurement_with_calendar_early(self):
        """Verify procurement behavior when the planned date is outside working hours,
        ensuring it adjusts correctly to the previous work interval."""
        values = {
            "date_planned": "2097-01-07 01:00:00",  # Monday outside working hour
            "warehouse_id": self.warehouse,
            "company_id": self.company,
            "rule_id": self.transfer_rule,
        }
        self.rule_obj.run(
            [
                self.rule_obj.Procurement(
                    self.product,
                    100,
                    self.product.uom_id,
                    self.warehouse.lot_stock_id,
                    "Test",
                    "Test",
                    self.warehouse.company_id,
                    values,
                )
            ]
        )
        move = self.move_obj.search([("product_id", "=", self.product.id)], limit=1)
        date = fields.Date.to_date(move.date)
        #  Expected date is Friday, 4th Jan 2097,
        #  due to the 1-day lead time and work calendar
        friday = fields.Date.to_date("2097-01-04 09:00:00")

        self.assertEqual(date, friday)

    def test_03_wh_plan_days_future(self):
        """Test the warehouse's planning tool to ensure correct
        future date computation with and without a working calendar."""
        reference = "2097-01-09 12:00:00"  # Wednesday
        # With calendar
        result = self.warehouse_2.wh_plan_days(reference, 3).date()
        # Expected result should skip the weekend and land on the next Monday
        next_monday = fields.Date.to_date("2097-01-14")
        self.assertEqual(result, next_monday)
        # Without calendar
        result = self.warehouse_3.wh_plan_days(reference, 3).date()
        # Expected result does not skip the weekend, landing on Saturday
        saturday = fields.Date.to_date("2097-01-12")
        self.assertEqual(result, saturday)

    def test_04_wh_plan_days_rounding(self):
        """Test the warehouse's planning tool to ensure correct
        future date computation when delta is a float and
        needs to be rounded."""
        reference = "2097-01-09 12:00:00"  # Wednesday
        # Case where delta is a float and needs rounding
        result = self.warehouse_2.wh_plan_days(reference, 2.5).date()
        # Should round 2.5 to 3 and return the correct date
        next_saturday = fields.Date.to_date("2097-01-11")
        self.assertEqual(result, next_saturday)

    def test_05_wh_plan_days_no_offset(self):
        """Test the warehouse's planning tool to ensure correct
        future date computation when delta is 0, meaning the date
        should remain unchanged."""
        reference = "2097-01-09 12:00:00"  # Wednesday
        # Case where delta is 0, so date_from should be returned as is
        result = self.warehouse_2.wh_plan_days(reference, 0).date()
        # Should return the same date as reference (Wednesday)
        self.assertEqual(result, fields.Date.to_date("2097-01-09"))

    @freeze_time("2097-01-11 09:00:00")
    def test_06_push_rule_with_calendar(self):
        """Test push rule triggers a new move with correct date via real
        push flow (picking-based).
        Frozen at 2097-01-11 09:00:00 (Friday) to test weekend handling.
        """
        # Verify no existing pushed moves
        pushed_move = self.move_obj.search(
            [
                ("location_id", "=", self.warehouse_2.lot_stock_id.id),
                ("location_dest_id", "=", self.wh2_bin_loc.id),
                ("product_id", "=", self.product.id),
            ],
            limit=1,
        )
        self.assertFalse(pushed_move)

        # Create a picking
        picking = self.picking_obj.create(
            {
                "picking_type_id": self.warehouse_2.int_type_id.id,
                "location_id": self.warehouse_2.wh_input_stock_loc_id.id,
                "location_dest_id": self.warehouse_2.lot_stock_id.id,
                "scheduled_date": "2097-01-11 09:00:00",
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 10,
                            "location_id": self.warehouse_2.wh_input_stock_loc_id.id,
                            "location_dest_id": self.warehouse_2.lot_stock_id.id,
                            "date": "2097-01-11 09:00:00",  # Friday
                        },
                    )
                ],
            }
        )
        # Confirm the picking
        picking.action_confirm()
        # Set the quantity and mark as done
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        # Validate the picking
        picking._action_done()

        # The push rule should create a new move from WH2 stock to WH2 bin
        pushed_move = self.move_obj.search(
            [
                ("location_id", "=", self.warehouse_2.lot_stock_id.id),
                ("location_dest_id", "=", self.wh2_bin_loc.id),
                ("product_id", "=", self.product.id),
            ],
            limit=1,
        )
        self.assertTrue(pushed_move, "No pushed move was created by the push rule!")
        self.assertEqual(pushed_move.rule_id, self.push_rule)
        self.assertEqual(
            pushed_move.date.date(),
            fields.Date.to_date("2097-01-14"),
            "Pushed move date should be Monday (skipping weekend)",
        )

    def test_07_push_rule_without_calendar(self):
        """Test push rule with warehouse that has no calendar."""
        # Create a move on Friday
        move = self.move_obj.create(
            {
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10,
                "location_id": self.warehouse_3.lot_stock_id.id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
                "date": "2097-01-11 09:00:00",  # Friday
            }
        )

        # Compute new date with push rule (should not skip weekend)
        new_date = self.push_rule_no_calendar._get_push_new_date(move)
        # Should be next day (Saturday) since there's no calendar
        expected_date = "2097-01-12 09:00:00"  # Saturday
        self.assertEqual(new_date, expected_date)

    def test_08_push_rule_zero_delay(self):
        """Test push rule with zero delay."""
        # Create a copy of the push rule with zero delay
        push_rule = self.push_rule.copy(
            {
                "name": "Push zero delay",
                "delay": 0,  # No delay
            }
        )

        # Create a move
        move_date = "2097-01-11 09:00:00"  # Friday
        move = self.move_obj.create(
            {
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10,
                "location_id": self.warehouse_2.lot_stock_id.id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
                "date": move_date,
            }
        )

        # Compute new date with push rule (should be same day)
        new_date = push_rule._get_push_new_date(move)
        self.assertEqual(new_date, move_date)
