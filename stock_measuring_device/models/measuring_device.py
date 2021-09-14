# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class MeasuringDevice(models.Model):
    _name = "measuring.device"
    _inherit = "collection.base"
    _description = "Measuring and Weighing Device"
    _order = "warehouse_id, name"

    name = fields.Char("Name", required=True)
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse", required=True)
    device_type = fields.Selection(
        selection=[],
        help="The type of device (e.g. zippcube, cubiscan...) "
        "depending on which module are installed.",
    )
    state = fields.Selection(
        [("not_ready", "Not Ready"), ("ready", "Ready")],
        default="not_ready",
        readonly=True,
        copy=False,
    )

    _sql_constraints = [
        (
            "name_uniq",
            "unique (name)",
            "The name of the measuring/weighing device must be unique.",
        ),
    ]

    def _get_measuring_device(self):
        with self.work_on(self._name) as work_ctx:
            return work_ctx.component(usage=self.device_type)

    def open_wizard(self):
        res = {
            "name": _("Measurement Wizard"),
            "res_model": "measuring.wizard",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "form",
            "context": {"default_device_id": self.id},
            "target": "fullscreen",
            "flags": {
                "withControlPanel": False,
                "form_view_initial_mode": "edit",
                "no_breadcrumbs": True,
            },
        }
        if self._is_being_used():
            pack = self.env["product.packaging"].search(
                [("measuring_device_id", "=", self.id)], limit=1
            )
            res["context"]["default_product_id"] = pack.product_id.id
        return res

    def _is_being_used(self):
        self.ensure_one()
        return bool(
            self.env["product.packaging"].search_count(
                [("measuring_device_id", "=", self.id)]
            )
        )

    def _update_packaging_measures(self, measures):
        self.ensure_one()
        measures = self._get_measuring_device().preprocess_measures(measures)
        line_domain = [
            ("wizard_id.device_id", "=", self.id),
            ("scan_requested", "=", True),
        ]

        packaging = self.env["product.packaging"]._measuring_device_find_assigned(self)
        if packaging:
            line_domain += [("packaging_id", "=", packaging.id)]
        else:
            line_domain += [
                ("packaging_id", "=", False),
                ("is_unit_line", "=", True),
            ]

        wizard_line = self.env["measuring.wizard.line"].search(
            line_domain,
            order="write_date DESC",
            limit=1,
        )
        if not wizard_line:
            _logger.warning("No wizard line found for this measure.")
            packaging.write(measures)
        else:
            measures.update({"scan_requested": False, "is_measured": True})
            wizard_line.write(measures)

        self._get_measuring_device().post_update_packaging_measures(
            measures, packaging, wizard_line
        )
        return packaging

    def test_device(self):
        for rec in self:
            success = rec._get_measuring_device().test_device()
            if success and rec.state == "not_ready":
                rec.state = "ready"
            elif not success and rec.state == "ready":
                rec.state = "not_ready"
