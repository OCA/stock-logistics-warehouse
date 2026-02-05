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

    def _get_next_reordering_date(self):
        self.ensure_one()
        now = fields.Datetime.now()
        calendar = self.orderpoint_calendar_id
        # TODO: should we take into account days off of the reordering calendar with
        #  'compute_leaves=True' here?
        return calendar and calendar.plan_hours(0, now) or now

    def _get_lead_date(self, date_order, lead_days):
        self.ensure_one()
        # Get the WH calendar
        calendar = self.calendar_id
        if not calendar:
            # No WH calendar defined => consume ``lead_days`` as solar days
            return fields.Datetime.add(date_order, days=lead_days or 0)
        if not lead_days:
            # Get the first workday for the WH calendar
            days = 1
            date_ref = date_order
        elif self.orderpoint_on_workday_policy == "skip_all_non_workdays":
            # Get the first workday for the WH calendar after consuming the
            # ``lead_days`` as workdays (for the WH calendar itself) starting
            # from the day after the reordering date itself
            days = lead_days
            date_ref = fields.Datetime.add(date_order, days=1)
        else:
            # Get the first workday for the WH calendar after consuming the
            # ``lead_days`` as solar days
            # (This is the behavior for policy ``skip_to_first_workday``, but
            # also a fallback in case the policy is not defined)
            days = 1
            date_ref = fields.Datetime.add(date_order, days=lead_days)
        return calendar.plan_days(days, date_ref, compute_leaves=True)
