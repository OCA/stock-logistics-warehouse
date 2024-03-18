# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestStockWarehouseCalendar(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
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
            {"name": "test product", "default_code": "PRD", "type": "product"}
        )

        route_vals = {"name": "WH2 -> WH"}
        cls.transfer_route = cls.env["stock.route"].create(route_vals)
        rule_vals = {
            "location_dest_id": cls.warehouse.lot_stock_id.id,
            "location_src_id": cls.warehouse_2.lot_stock_id.id,
            "action": "pull_push",
            "warehouse_id": cls.warehouse.id,
            "propagate_warehouse_id": cls.warehouse_2.id,
            "picking_type_id": cls.env.ref("stock.picking_type_internal").id,
            "name": "WH2->WH",
            "route_id": cls.transfer_route.id,
            "delay": 1,
        }
        cls.transfer_rule = cls.env["stock.rule"].create(rule_vals)
        cls.product.route_ids = [(6, 0, cls.transfer_route.ids)]

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
