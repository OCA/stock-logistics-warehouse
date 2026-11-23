# Copyright 2026 Camptocamp SA
# @author Hadrien Huvelle <hadrien.huvelle@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import new_test_user

from .common import InventoryReportCommon


class TestInventoryReportSecurity(InventoryReportCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_company = cls.env["res.company"].create(
            {"name": "Inventory Report Security Company"}
        )
        cls.other_warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.other_company.id)], limit=1
        )
        cls.stock_manager_user = new_test_user(
            cls.env,
            login="inventory_stock_manager",
            groups="base.group_user,stock.group_stock_manager",
            company_id=cls.env.company.id,
            company_ids=[Command.set([cls.env.company.id])],
        )
        cls.report_company_a = (
            cls.env["stock.external.inventory.report"]
            .sudo()
            .create(
                {
                    "warehouse_id": cls.warehouse.id,
                    "company_id": cls.env.company.id,
                    "discrepancy_user_id": cls.env.user.id,
                }
            )
        )
        cls.report_company_b = (
            cls.env["stock.external.inventory.report"]
            .sudo()
            .create(
                {
                    "warehouse_id": cls.other_warehouse.id,
                    "company_id": cls.other_company.id,
                    "discrepancy_user_id": cls.env.user.id,
                }
            )
        )
        cls.line_company_a = (
            cls.env["stock.external.inventory.report.line"]
            .sudo()
            .create(
                {
                    "report_id": cls.report_company_a.id,
                    "external_product_code": "SEC-A",
                    "external_qty": 1.0,
                }
            )
        )
        cls.line_company_b = (
            cls.env["stock.external.inventory.report.line"]
            .sudo()
            .create(
                {
                    "report_id": cls.report_company_b.id,
                    "external_product_code": "SEC-B",
                    "external_qty": 1.0,
                }
            )
        )

    def test_reports_are_scoped_by_allowed_companies(self):
        reports = self.env["stock.external.inventory.report"].with_user(
            self.stock_manager_user
        )
        self.assertEqual(
            reports.search_count([("id", "=", self.report_company_a.id)]), 1
        )
        self.assertEqual(
            reports.search_count([("id", "=", self.report_company_b.id)]), 0
        )

    def test_lines_are_scoped_by_allowed_companies(self):
        lines = self.env["stock.external.inventory.report.line"].with_user(
            self.stock_manager_user
        )
        self.assertEqual(lines.search_count([("id", "=", self.line_company_a.id)]), 1)
        self.assertEqual(lines.search_count([("id", "=", self.line_company_b.id)]), 0)
