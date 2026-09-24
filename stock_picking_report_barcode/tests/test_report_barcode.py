# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestReportBarcode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type = cls.warehouse.in_type_id
        cls.picking_type.display_picking_barcode = True
        cls.picking_type.display_report_picking_barcode = True

    def _create_picking(self):
        return (
            self.env["stock.picking"]
            .with_context(default_picking_type_id=self.picking_type.id)
            .create({})
        )

    def test_report_contains_barcode(self):
        picking = self._create_picking()
        report = self.env["ir.actions.report"]._render_qweb_html(
            "stock.action_report_delivery", picking.ids
        )
        html_content = report[0].decode()
        self.assertIn("Picking Barcode", html_content)

    def test_report_no_barcode_when_report_disabled(self):
        self.picking_type.display_report_picking_barcode = False
        picking = self._create_picking()
        report = self.env["ir.actions.report"]._render_qweb_html(
            "stock.action_report_delivery", picking.ids
        )
        html_content = report[0].decode()
        self.assertNotIn("Picking Barcode", html_content)

    def test_report_no_barcode_when_form_enabled_but_report_disabled(self):
        """Form barcode enabled but report barcode disabled: no barcode on report."""
        self.picking_type.display_picking_barcode = True
        self.picking_type.display_report_picking_barcode = False
        picking = self._create_picking()
        report = self.env["ir.actions.report"]._render_qweb_html(
            "stock.action_report_delivery", picking.ids
        )
        html_content = report[0].decode()
        self.assertNotIn("Picking Barcode", html_content)
