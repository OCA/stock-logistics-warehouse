# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestStockWarehouseCalendar(TransactionCase):
    def setUp(self):
        super(TestStockWarehouseCalendar, self).setUp()
        self.wh_obj = self.env["stock.warehouse"]
        self.move_obj = self.env["stock.move"]
        self.pg_obj = self.env["procurement.group"]

        self.company = self.env.ref("base.main_company")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.customer_loc = self.env.ref("stock.stock_location_customers")
        self.company_partner = self.env.ref("base.main_partner")
        self.calendar = self.env.ref("resource.resource_calendar_std")
        self.warehouse.calendar_id = self.calendar
        self.warehouse_2 = self.wh_obj.create(
            {"code": "WH-T", "name": "Warehouse Test", "calendar_id": self.calendar.id}
        )
        self.warehouse_3 = self.wh_obj.create(
            {"code": "WH-no-calendar", "name": "Warehouse Test 2"}
        )

        self.product = self.env["product.product"].create(
            {"name": "test product", "default_code": "PRD", "type": "product"}
        )

        route_vals = {"name": "WH2 -> WH"}
        self.transfer_route = self.env["stock.location.route"].create(route_vals)
        rule_vals = {
            "location_id": self.warehouse.lot_stock_id.id,
            "location_src_id": self.warehouse_2.lot_stock_id.id,
            "action": "pull_push",
            "warehouse_id": self.warehouse.id,
            "propagate_warehouse_id": self.warehouse_2.id,
            "picking_type_id": self.env.ref("stock.picking_type_internal").id,
            "name": "WH2->WH",
            "route_id": self.transfer_route.id,
            "delay": 1,
        }
        self.transfer_rule = self.env["stock.rule"].create(rule_vals)
        self.product.route_ids = [(6, 0, self.transfer_route.ids)]

    def test_01_procurement_with_calendar(self):
        values = {
            "date_planned": "2097-01-07 09:00:00",  # Monday
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
        # Friday 4th Jan 2017
        friday = fields.Date.to_date("2097-01-04 09:00:00")

        self.assertEqual(date, friday)

    def test_02_procurement_with_calendar_early(self):
        """Test procuring at the beginning of the day, with no work intervals
        before."""
        values = {
            "date_planned": "2097-01-07 01:00:00",  # Monday
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
        # Friday 4th Jan 2017
        friday = fields.Date.to_date("2097-01-04 09:00:00")

        self.assertEqual(date, friday)

    def test_03_wh_plan_days_future(self):
        """Test plan days helper in warehouse."""
        reference = "2097-01-09 12:00:00"  # Wednesday
        # With calendar
        result = self.warehouse_2.wh_plan_days(reference, 3).date()
        next_monday = fields.Date.to_date("2097-01-14")
        self.assertEqual(result, next_monday)
        # Without calendar
        result = self.warehouse_3.wh_plan_days(reference, 3).date()
        saturday = fields.Date.to_date("2097-01-12")
        self.assertEqual(result, saturday)
