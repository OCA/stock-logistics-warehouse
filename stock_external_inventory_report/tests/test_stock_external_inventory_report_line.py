# Copyright 2026 Camptocamp SA
# @author Hadrien Huvelle <hadrien.huvelle@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.exceptions import UserError
from odoo.fields import Command

from .common import InventoryReportCommon


class TestStockExternalInventoryReportLine(InventoryReportCommon):
    def _new_report(self):
        return self.env["stock.external.inventory.report"].create(
            {"warehouse_id": self.warehouse.id, "report_date": datetime(2026, 1, 1)}
        )

    def test_get_location_from_stock_type_mapping(self):
        """The stock types are the warehouse ones, empty is the free one."""
        line = self.env["stock.external.inventory.report.line"]
        self.assertEqual(
            line._get_location_from_stock_type(self.warehouse, "free"),
            self.warehouse.lot_stock_id,
        )
        self.assertEqual(
            line._get_location_from_stock_type(self.warehouse, ""),
            self.warehouse.lot_stock_id,
        )
        self.assertEqual(
            line._get_location_from_stock_type(self.warehouse, " Quality "),
            self.warehouse.wh_qc_stock_loc_id,
        )

    def test_get_location_from_stock_type_unknown_raises(self):
        line = self.env["stock.external.inventory.report.line"]
        with self.assertRaisesRegex(UserError, "Unrecognized stock type"):
            line._get_location_from_stock_type(self.warehouse, "mystery")

    def test_resolve_external_values_marks_missing_product(self):
        report = self._new_report()
        line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": report.id,
                "external_product_code": "UNKNOWN-CODE",
                "external_qty": 2.0,
                "stock_type": "free",
            }
        )

        line._resolve_external_values(self.warehouse)

        self.assertTrue(line.product_not_found)
        self.assertIn("Product not found", line.note)
        self.assertFalse(line.product_id)

    def test_resolve_external_values_resolves_product_lot_location_and_snapshot(self):
        report = self._new_report()
        lot = self.env["stock.lot"].create(
            {"product_id": self.product_lot.id, "name": "LOCK-LOT-01"}
        )
        quality_location = self.warehouse.wh_qc_stock_loc_id
        self.env["stock.quant"]._update_available_quantity(
            self.product_lot,
            quality_location,
            7.0,
            lot_id=lot,
        )

        line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": report.id,
                "external_product_code": self.product_lot.default_code,
                "external_qty": 10.0,
                "stock_type": "quality",
                "external_lot_name": "LOCK-LOT-01",
                "external_date_mark": "20261231",
            }
        )

        line._resolve_external_values(self.warehouse)

        self.assertEqual(line.product_id, self.product_lot)
        self.assertEqual(line.location_id, quality_location)
        self.assertEqual(line.odoo_qty, 7.0)
        self.assertEqual(line.unit_cost, self.product_lot.standard_price)
        self.assertEqual(line.lot_id.name, "LOCK-LOT-01")
        self.assertIn("date_mark=20261231", line.note)

    def test_apply_stock_overwrite_skips_unresolved_line(self):
        report = self._new_report()
        line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": report.id,
                "external_product_code": "UNKNOWN",
                "external_qty": 5.0,
                "stock_type": "free",
            }
        )

        result = line.action_apply_stock_overwrite()

        self.assertEqual(line.line_state, "new")
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "display_notification")
        self.assertIn("1 line(s) skipped", result["params"]["title"])
        self.assertIn("UNKNOWN", result["params"]["message"])

    def test_apply_stock_overwrite_bulk_skips_unresolved_and_applies_resolved(self):
        report = self._new_report()
        resolved_line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": report.id,
                "external_product_code": self.product.default_code,
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "external_qty": 6.0,
                "odoo_qty": 1.0,
            }
        )
        unresolved_line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": report.id,
                "external_product_code": "UNKNOWN",
                "external_qty": 5.0,
                "stock_type": "free",
            }
        )
        lines = resolved_line | unresolved_line

        result = lines.action_apply_stock_overwrite()

        self.assertEqual(resolved_line.line_state, "applied")
        self.assertEqual(unresolved_line.line_state, "new")
        self.assertEqual(result["tag"], "display_notification")
        self.assertIn("UNKNOWN", result["params"]["message"])

    def test_apply_stock_overwrite_active_domain_fallback_when_nothing_selected(self):
        other_report = self._new_report()
        untouched_line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": other_report.id,
                "external_product_code": self.product_2.default_code,
                "product_id": self.product_2.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "external_qty": 9.0,
                "odoo_qty": 0.0,
            }
        )
        report = self._new_report()
        line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": report.id,
                "external_product_code": self.product.default_code,
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "external_qty": 4.0,
                "odoo_qty": 0.0,
            }
        )

        empty_lines = self.env["stock.external.inventory.report.line"].with_context(
            active_domain=[("id", "=", line.id)]
        )
        empty_lines.action_apply_stock_overwrite()

        self.assertEqual(line.line_state, "applied")
        self.assertEqual(untouched_line.line_state, "new")

    def test_apply_stock_overwrite_empty_recordset_without_active_domain_is_noop(self):
        # Guards against the report-level "Apply Stock Overwrite" button (which
        # calls this method with a pre-filtered, possibly-empty recordset and
        # no `active_domain` in context) ever falling back to searching and
        # applying every line in the database.
        report = self._new_report()
        untouched_line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": report.id,
                "external_product_code": self.product.default_code,
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "external_qty": 4.0,
                "odoo_qty": 0.0,
            }
        )

        result = self.env[
            "stock.external.inventory.report.line"
        ].action_apply_stock_overwrite()

        self.assertTrue(result)
        self.assertEqual(untouched_line.line_state, "new")

    def test_apply_stock_overwrite_zero_delta_marks_reviewed(self):
        report = self._new_report()
        line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": report.id,
                "external_product_code": self.product.default_code,
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "external_qty": 3.0,
                "odoo_qty": 3.0,
            }
        )

        line.action_apply_stock_overwrite()

        self.assertEqual(line.line_state, "reviewed")
        self.assertTrue(line.reviewed_at)

    def test_apply_stock_overwrite_delta_updates_quant_and_marks_applied(self):
        report = self._new_report()
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.warehouse.lot_stock_id,
            1.0,
        )
        line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": report.id,
                "external_product_code": self.product.default_code,
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "external_qty": 6.0,
                "odoo_qty": 1.0,
            }
        )

        line.action_apply_stock_overwrite()

        self.assertEqual(line.line_state, "applied")
        self.assertTrue(line.reviewed_at)

        qty = self.env["stock.quant"]._get_available_quantity(
            self.product,
            self.warehouse.lot_stock_id,
        )
        self.assertEqual(qty, 6.0)
        move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("is_inventory", "=", True),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(move)
        self.assertEqual(move.quantity, 5.0)

    def test_apply_stock_overwrite_without_existing_quant_creates_inventory_adjustment(
        self,
    ):
        report = self._new_report()
        line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": report.id,
                "external_product_code": self.product.default_code,
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "external_qty": 4.0,
                "odoo_qty": 0.0,
            }
        )

        line.action_apply_stock_overwrite()

        qty = self.env["stock.quant"]._get_available_quantity(
            self.product,
            self.warehouse.lot_stock_id,
        )
        self.assertEqual(qty, 4.0)
        move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("is_inventory", "=", True),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(move)
        self.assertEqual(move.quantity, 4.0)

    def test_obsolete_report_restrictions_on_line_write_and_unlink(self):
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
        line = report.line_ids
        report.action_set_obsolete()

        with self.assertRaisesRegex(UserError, "cannot be modified"):
            line.write({"external_qty": 9.0})

        with self.assertRaisesRegex(UserError, "cannot be deleted"):
            line.unlink()

    def _new_costed_product(self, code, cost):
        return self.env["product.product"].create(
            {
                "name": f"Costed Product {code}",
                "default_code": code,
                "type": "consu",
                "is_storable": True,
                "standard_price": cost,
            }
        )

    def test_unit_cost_keeps_all_digits_when_read_back(self):
        product = self._new_costed_product("INV-CHEAP-001", 0.003456)
        line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": self._new_report().id,
                "external_product_code": product.default_code,
                "external_qty": 1.0,
            }
        )

        # Regression guard: read the cost back from the database. The cache
        # still holds the unrounded cost, so without this the test would pass
        # even if the stored value were rounded again.
        line.invalidate_recordset()

        self.assertEqual(line.unit_cost, 0.003456)

    def test_resolve_external_values_keeps_all_unit_cost_digits(self):
        product = self._new_costed_product("INV-CHEAP-002", 1.234567)
        line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": self._new_report().id,
                "external_product_code": product.default_code,
                "external_qty": 1.0,
                "stock_type": "free",
            }
        )

        line._resolve_external_values(self.warehouse)
        line.invalidate_recordset()

        self.assertEqual(line.unit_cost, 1.234567)

    def test_variance_amount_uses_all_unit_cost_digits_after_recompute(self):
        product = self._new_costed_product("INV-CHEAP-003", 0.003456)
        line = self.env["stock.external.inventory.report.line"].create(
            {
                "report_id": self._new_report().id,
                "external_product_code": product.default_code,
                "external_qty": 10000.0,
                "odoo_qty": 0.0,
            }
        )
        line.invalidate_recordset()

        line.odoo_qty = 4000.0
        line.invalidate_recordset()

        # 6000 x 0.003456 = 20.736, rounded to the cent.
        self.assertEqual(line.variance_amount, 20.74)

    def test_cost_below_one_cent_is_not_flagged_as_zero_cost(self):
        product = self._new_costed_product("INV-CHEAP-004", 0.003456)
        report = self._new_report()
        cheap_line, no_cost_line = self.env[
            "stock.external.inventory.report.line"
        ].create(
            [
                {
                    "report_id": report.id,
                    "external_product_code": product.default_code,
                    "external_qty": 1.0,
                },
                {
                    "report_id": report.id,
                    "external_product_code": self.product_2.default_code,
                    "external_qty": 1.0,
                },
            ]
        )

        self.assertFalse(cheap_line.zero_standard_price)
        self.assertTrue(no_cost_line.zero_standard_price)
