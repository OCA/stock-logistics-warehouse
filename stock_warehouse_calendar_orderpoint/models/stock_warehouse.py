# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    orderpoint_calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Reordering Calendar",
        default=lambda o: o._default_orderpoint_calendar_id(),
        help="Calendar used to compute the lead date of reordering rules",
    )
    orderpoint_on_workday_policy = fields.Selection(
        [
            ("skip_to_first_workday", "Skip to first workday"),
            ("skip_all_non_workdays", "Skip non-workdays"),
        ],
        string="Reordering on Workday Policy",
        default=lambda o: o._default_orderpoint_on_workday_policy(),
        help="Policy to postpone the lead date to the first available workday:\n"
        "* skip to first workday: compute the date using lead delay days as solar"
        " days, then skip to the next workday if the result is not a workday"
        " (eg: run action on Friday with 2 days lead delay -> the result is Sunday ->"
        " skip to the first following workday, Monday)\n"
        "* skip non-workdays: compute the order date consuming lead delay days only on"
        " (eg: run action on Friday with 2 days lead delay -> skip Saturday and Sunday"
        " -> start consuming lead days on Monday as first lead day -> the result is"
        " Tuesday)",
    )

    def get_company_from_ctx(self):
        company = self.env.company
        if self.env.context.get("force_wh_company"):
            company = (
                self.env["res.company"]
                .browse(self.env.context["force_wh_company"])
                .exists()
            )
        return company

    def _default_orderpoint_calendar_id(self):
        company = self.get_company_from_ctx()
        return company.orderpoint_calendar_id

    def _default_orderpoint_on_workday_policy(self):
        company = self.get_company_from_ctx()
        return company.orderpoint_on_workday_policy

    @api.model
    def create(self, vals):
        # We want to propagate the company_id in the case when we create a new company
        # and a corresponding WH is being created as a result.
        if vals.get("company_id"):
            self = self.with_context(force_wh_company=vals["company_id"])
        return super().create(vals)
