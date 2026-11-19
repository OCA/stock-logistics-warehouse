# Copyright 2026 Camptocamp SA
# @author Hadrien Huvelle <hadrien.huvelle@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.fields import Command

from ..models.stock_external_inventory_report import (
    ACTIVITY_DISCREPANCY,
    ACTIVITY_MISSING_PRODUCT,
    ACTIVITY_ZERO_COST,
    StockExternalInventoryReport,
)
from .common import InventoryReportCommon


class TestStockExternalInventoryReport(InventoryReportCommon):
    def test_create_obsoletes_previous_new_report(self):
        report_model = self.env["stock.external.inventory.report"]
        first = report_model.create(
            {
                "warehouse_id": self.warehouse.id,
                "report_date": datetime(2026, 1, 1),
                "line_ids": [
                    Command.create(
                        {"external_product_code": "INV-001", "external_qty": 1.0}
                    )
                ],
            }
        )
        self.assertEqual(first.state, "new")

        second = report_model.create(
            {
                "warehouse_id": self.warehouse.id,
                "report_date": datetime(2026, 1, 2),
                "line_ids": [
                    Command.create(
                        {"external_product_code": "INV-001", "external_qty": 2.0}
                    )
                ],
            }
        )
        self.assertEqual(second.state, "new")
        self.assertEqual(first.state, "obsolete")

    def test_create_keeps_new_reports_of_other_warehouses(self):
        """A report only obsoletes the pending reports of its own warehouse."""
        report_model = self.env["stock.external.inventory.report"]
        other_warehouse = self.env["stock.warehouse"].create(
            {"name": "Other External Warehouse", "code": "OEWH"}
        )
        first = report_model.create({"warehouse_id": self.warehouse.id})
        second = report_model.create({"warehouse_id": other_warehouse.id})
        self.assertEqual((first.state, second.state), ("new", "new"))

    def test_action_mark_processed_requires_all_lines_reviewed(self):
        report = self.env["stock.external.inventory.report"].create(
            {
                "warehouse_id": self.warehouse.id,
                "report_date": datetime(2026, 1, 10),
                "line_ids": [
                    Command.create(
                        {"external_product_code": "INV-001", "external_qty": 1.0}
                    ),
                    Command.create(
                        {
                            "external_product_code": "INV-002",
                            "external_qty": 2.0,
                            "line_state": "reviewed",
                        },
                    ),
                ],
            }
        )

        with self.assertRaisesRegex(UserError, "All lines must be reviewed"):
            report.action_mark_processed()

        report.line_ids.filtered(
            lambda line: line.line_state == "new"
        ).action_mark_reviewed()
        report.action_mark_processed()
        self.assertEqual(report.state, "processed")

    def test_schedule_discrepancy_activities_creates_three_categories(self):
        report = self.env["stock.external.inventory.report"].create(
            {
                "warehouse_id": self.warehouse.id,
                "report_date": datetime(2026, 1, 10),
                "line_ids": [
                    Command.create(
                        {
                            "external_product_code": "INV-001",
                            "external_qty": 30.0,
                            "product_id": self.product.id,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "odoo_qty": 0.0,
                            "unit_cost": 10.0,
                        },
                    ),
                    Command.create(
                        {
                            "external_product_code": "INV-002",
                            "external_qty": 5.0,
                            "product_id": self.product_2.id,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "odoo_qty": 0.0,
                            "unit_cost": 0.0,
                        },
                    ),
                    Command.create(
                        {
                            "external_product_code": "MISSING-001",
                            "external_qty": 8.0,
                            "product_not_found": True,
                        },
                    ),
                ],
            }
        )

        report._schedule_discrepancy_activities()

        activities = self._activities_for_report(report)
        activity_types = report._get_activity_types()
        self.assertEqual(
            activities.activity_type_id,
            activity_types[ACTIVITY_DISCREPANCY]
            | activity_types[ACTIVITY_ZERO_COST]
            | activity_types[ACTIVITY_MISSING_PRODUCT],
        )
        self.assertEqual(len(activities), 3)

    def test_create_does_not_schedule_activities_before_line_resolution(self):
        report = self.env["stock.external.inventory.report"].create(
            {
                "warehouse_id": self.warehouse.id,
                "report_date": datetime(2026, 1, 10),
                "line_ids": [
                    Command.create(
                        {"external_product_code": "INV-001", "external_qty": 30.0}
                    ),
                ],
            }
        )

        self.assertFalse(self._activities_for_report(report))

    def test_create_schedules_activities_for_resolved_lines(self):
        report = self.env["stock.external.inventory.report"].create(
            {
                "warehouse_id": self.warehouse.id,
                "report_date": datetime(2026, 1, 10),
                "line_ids": [
                    Command.create(
                        {
                            "external_product_code": "INV-001",
                            "external_qty": 30.0,
                            "product_id": self.product.id,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "odoo_qty": 0.0,
                            "unit_cost": 10.0,
                        },
                    ),
                ],
            }
        )

        activities = self._activities_for_report(report)
        self.assertEqual(
            activities.activity_type_id,
            report._get_activity_types()[ACTIVITY_DISCREPANCY],
        )

    def test_comparison_error_fields_writable_on_obsolete_report(self):
        # Regression test: found live via manual UI testing. A report can
        # become obsolete mid-flight (a newer report obsoletes any other
        # 'new' report for the same company, see `create()`), and job 2 may
        # still be running against it. `write()` blocks nearly all field
        # writes on an obsolete report -- the comparison-error fields must
        # be exempted, otherwise `_write_comparison_error` itself raises
        # ("Obsolete inventory reports cannot be modified"), clobbering the
        # original exception instead of letting it propagate.
        report = self.env["stock.external.inventory.report"].create(
            {"warehouse_id": self.warehouse.id, "report_date": datetime(2026, 1, 20)}
        )
        report.action_set_obsolete()

        report.write({"comparison_has_error": True, "comparison_error_message": "boom"})

        self.assertTrue(report.comparison_has_error)
        self.assertEqual(report.comparison_error_message, "boom")

    def test_job_process_comparisons_reraises_error_when_report_becomes_obsolete(
        self,
    ):
        report = self.env["stock.external.inventory.report"].create(
            {
                "warehouse_id": self.warehouse.id,
                "report_date": datetime(2026, 1, 20),
                "line_ids": [
                    Command.create(
                        {"external_product_code": "INV-001", "external_qty": 1.0}
                    )
                ],
            }
        )
        report.action_set_obsolete()

        def _fake_write_comparison_error(self, message):
            self.write(
                {"comparison_has_error": True, "comparison_error_message": message}
            )

        with patch.object(
            type(report), "_write_comparison_error", _fake_write_comparison_error
        ):
            # Specifically the *line*-level guard ("Lines linked to obsolete
            # inventory reports cannot be modified"), not the report-level
            # one ("Obsolete inventory reports cannot be modified") that the
            # write()-allowlist fix above prevents `_write_comparison_error`
            # from raising instead. A looser match would pass even if that
            # fix were reverted.
            with self.assertRaisesRegex(UserError, "Lines linked to obsolete"):
                report._process_comparisons_and_alerts()

        self.assertTrue(report.comparison_has_error)
        self.assertIn("Lines linked to obsolete", report.comparison_error_message)

    def test_job_process_comparisons_and_alerts_flags_report_on_failure(self):
        report = self.env["stock.external.inventory.report"].create(
            {
                "warehouse_id": self.warehouse.id,
                "report_date": datetime(2026, 1, 15),
                "line_ids": [
                    Command.create(
                        {"external_product_code": "INV-001", "external_qty": 1.0}
                    )
                ],
            }
        )

        # The line resolution fails (patched below), exercising the job-2
        # failure path.
        #
        # `_write_comparison_error` itself uses a genuinely separate DB
        # cursor (see models/stock_external_inventory_report.py) so the flag survives
        # the transaction rollback that queue_job's HTTP job runner performs
        # in production. That separate cursor cannot see this test's own
        # uncommitted `report` row under Postgres read-committed isolation,
        # so it is patched here to a same-transaction write -- this test
        # verifies the orchestration (called with the right message,
        # re-raises, clears on a later success), not cross-process
        # durability of the separate cursor itself.
        def _fake_write_comparison_error(self, message):
            self.write(
                {"comparison_has_error": True, "comparison_error_message": message}
            )

        def _failing_resolve(self, warehouse):
            raise ValueError("Resolution failed")

        with patch.object(
            type(report), "_write_comparison_error", _fake_write_comparison_error
        ):
            with (
                patch.object(
                    type(report.line_ids), "_resolve_external_values", _failing_resolve
                ),
                self.assertRaisesRegex(ValueError, "Resolution failed"),
            ):
                report._process_comparisons_and_alerts()

            self.assertTrue(report.comparison_has_error)
            self.assertEqual(report.comparison_error_message, "Resolution failed")

            # Rerun once the cause is gone: the error flags must self-clear
            # on success.
            report._process_comparisons_and_alerts()

        self.assertFalse(report.comparison_has_error)
        self.assertFalse(report.comparison_error_message)

    def test_write_blocks_obsolete_reports(self):
        report = self.env["stock.external.inventory.report"].create(
            {
                "warehouse_id": self.warehouse.id,
                "report_date": datetime(2026, 1, 10),
                "line_ids": [
                    Command.create(
                        {"external_product_code": "INV-001", "external_qty": 1.0}
                    )
                ],
            }
        )
        report.action_set_obsolete()

        with self.assertRaisesRegex(UserError, "Obsolete inventory reports cannot"):
            report.write({"external_reference": "FORBIDDEN"})

        # State write remains allowed.
        report.write({"state": "obsolete"})

    def test_discrepancy_threshold(self):
        """A line is over the threshold given by `_get_discrepancy_threshold`."""
        report = self._create_report()
        line_vals = {
            "report_id": report.id,
            "external_product_code": "INV-001",
            "external_qty": 1.0,
            "unit_cost": 10.0,
        }
        line_model = self.env["stock.external.inventory.report.line"]
        # Stored computed fields are computed when read: read each flag with
        # its threshold
        default_line = line_model.create(line_vals)
        self.assertEqual(default_line.variance_amount, 10.0)
        self.assertFalse(default_line.over_threshold)
        with patch.object(
            type(self.env["stock.external.inventory.report"]),
            "_get_discrepancy_threshold",
            return_value=5.0,
        ):
            low_threshold_line = line_model.create(line_vals)
            self.assertTrue(low_threshold_line.over_threshold)

    def test_create_obsoletes_reports_of_each_warehouse(self):
        """New reports obsolete the pending ones of their warehouses."""
        report_model = self.env["stock.external.inventory.report"]
        other_warehouse = self.env["stock.warehouse"].create(
            {"name": "Other External Warehouse 2", "code": "OEW2"}
        )
        old_reports = report_model.create(
            [
                {"warehouse_id": self.warehouse.id},
                {"warehouse_id": other_warehouse.id},
            ]
        )
        new_reports = report_model.create(
            [
                {"warehouse_id": self.warehouse.id},
                {"warehouse_id": other_warehouse.id},
            ]
        )
        self.assertEqual(set(old_reports.mapped("state")), {"obsolete"})
        self.assertEqual(set(new_reports.mapped("state")), {"new"})

    def test_activity_types_by_kind(self):
        """Each kind of activity has its own activity type on the report model."""
        activity_types = self.env[
            "stock.external.inventory.report"
        ]._get_activity_types()
        self.assertEqual(
            set(activity_types),
            {ACTIVITY_DISCREPANCY, ACTIVITY_ZERO_COST, ACTIVITY_MISSING_PRODUCT},
        )
        self.assertEqual(
            set(activity_types[ACTIVITY_DISCREPANCY].mapped("res_model")),
            {"stock.external.inventory.report"},
        )

    def test_action_process_comparisons(self):
        """The button runs the comparison of the report."""
        report = self._create_report()
        with patch.object(
            type(report), "process_comparisons_and_alerts", autospec=True
        ) as compare:
            report.action_process_comparisons()
        compare.assert_called_once_with(report)

    def test_process_comparisons_and_alerts(self):
        """The comparison runs right away by default."""
        report = self._create_report()
        with patch.object(
            type(report), "_process_comparisons_and_alerts", autospec=True
        ) as compare:
            # This module's implementation, whatever overrides it (e.g. the
            # queue module's)
            StockExternalInventoryReport.process_comparisons_and_alerts(report)
        compare.assert_called_once_with(report)
