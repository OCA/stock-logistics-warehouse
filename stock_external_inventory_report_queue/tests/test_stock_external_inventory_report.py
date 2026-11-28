# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.queue_job.tests.common import trap_jobs
from odoo.addons.stock_external_inventory_report.tests.common import (
    InventoryReportCommon,
)


class TestStockExternalInventoryReportQueue(InventoryReportCommon):
    """The comparison of a report runs in a job."""

    def test_process_comparisons_and_alerts(self):
        """The comparison of each report is a job."""
        reports = self._create_report() | self._create_report()
        with trap_jobs() as trap:
            reports.process_comparisons_and_alerts()
        trap.assert_jobs_count(2)
        for report in reports:
            trap.assert_enqueued_job(
                report._process_comparisons_and_alerts,
                properties={
                    "description": f"Process inventory comparisons for {report.name}"
                },
            )
        with patch.object(
            type(reports), "_process_comparisons_and_alerts", autospec=True
        ) as compare:
            trap.perform_enqueued_jobs()
        self.assertEqual(compare.call_count, 2)

    def test_action_process_comparisons(self):
        """The button schedules the comparison and tells the user."""
        report = self._create_report()
        with trap_jobs() as trap:
            action = report.action_process_comparisons()
        trap.assert_jobs_count(1)
        self.assertEqual(action["tag"], "display_notification")

    def test_comparison_jobs(self):
        """The smart button lists the comparison jobs of the report."""
        report = self._create_report()
        other_report = self._create_report()
        report.with_delay()._process_comparisons_and_alerts()
        other_report.with_delay()._process_comparisons_and_alerts()
        self.assertEqual(report.comparison_job_count, 1)
        action = report.action_view_comparison_jobs()
        jobs = self.env["queue.job"].search(action["domain"])
        self.assertEqual(jobs.records, report)

    def test_job_function(self):
        """The comparison has its job function, to configure the jobs."""
        job_function = self.env.ref(
            "stock_external_inventory_report_queue."
            "job_function_stock_external_inventory_report_process_comparisons_and_alerts"
        )
        self.assertEqual(
            job_function.name,
            "<stock.external.inventory.report>._process_comparisons_and_alerts",
        )
