# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestStockWarehouseCalendar(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh_obj = cls.env["stock.warehouse"]
        cls.move_obj = cls.env["stock.move"]
        cls.pg_obj = cls.env["procurement.group"]

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

        cls.product = cls.env["product.product"].create(
            {"name": "test product", "default_code": "PRD", "is_storable": True}
        )

        route_vals = {"name": "WH-T -> WH"}
        cls.transfer_route = cls.env["stock.route"].create(route_vals)
        rule_vals = {
            "location_dest_id": cls.warehouse.lot_stock_id.id,
            "location_src_id": cls.warehouse_2.lot_stock_id.id,
            "action": "pull_push",
            "warehouse_id": cls.warehouse.id,
            "propagate_warehouse_id": cls.warehouse_2.id,
            "picking_type_id": cls.env.ref("stock.picking_type_internal").id,
            "name": "WH-T->WH",
            "route_id": cls.transfer_route.id,
            "delay": 1,
        }
        cls.transfer_rule = cls.env["stock.rule"].create(rule_vals)
        cls.product.route_ids = [(6, 0, cls.transfer_route.ids)]

    def test_01_procurement_with_calendar(self):
        """Ensure procurement respects the company's working calendar
        when calculating the planned stock move date."""
        values = {
            "date_planned": "2097-01-07 09:00:00",  # Monday inside working hours
            "warehouse_id": self.warehouse,
            "company_id": self.company,
            "rule_id": self.transfer_rule,
        }
        self.pg_obj.run(
            [
                self.pg_obj.Procurement(
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
        move = self.env["stock.move"].search(
            [("product_id", "=", self.product.id)], limit=1
        )
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
        self.pg_obj.run(
            [
                self.pg_obj.Procurement(
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
        move = self.env["stock.move"].search(
            [("product_id", "=", self.product.id)], limit=1
        )
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
