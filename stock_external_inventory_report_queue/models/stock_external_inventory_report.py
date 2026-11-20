# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockExternalInventoryReport(models.Model):
    _inherit = "stock.external.inventory.report"

    comparison_job_count = fields.Integer(compute="_compute_comparison_job_count")

    def _compute_comparison_job_count(self):
        for report in self:
            report.comparison_job_count = self.env["queue.job"].search_count(
                report._get_comparison_job_domain()
            )

    def _get_comparison_job_domain(self):
        """Return the domain of the comparison jobs of the report."""
        self.ensure_one()
        return [
            ("model_name", "=", self._name),
            ("func_string", "like", f"{self._name}({self.id},)"),
        ]

    @api.private
    def process_comparisons_and_alerts(self):
        # OVERRIDE: run the comparison of each report in a job, configured by
        # the job function of `_process_comparisons_and_alerts`
        for report in self:
            report.with_delay(
                description=self.env._(
                    "Process inventory comparisons for %(name)s", name=report.name
                )
            )._process_comparisons_and_alerts()
        return True

    def action_process_comparisons(self):
        # OVERRIDE: tell the user the comparison runs in a job
        super().action_process_comparisons()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "info",
                "message": self.env._(
                    "The comparison is scheduled: it runs in a job, the report "
                    "will be updated when it is done."
                ),
                "next": {"type": "ir.actions.act_window_close"},
            },
        }

    def action_view_comparison_jobs(self):
        """Smart button: the comparison jobs of the report."""
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "queue_job.action_queue_job"
        )
        action["domain"] = self._get_comparison_job_domain()
        action["context"] = {}
        return action
