# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)


from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.depends(
        "rule_ids",
        "product_id.seller_ids",
        "product_id.seller_ids.delay",
        "warehouse_id.orderpoint_calendar_id",
        "warehouse_id.orderpoint_on_workday_policy",
    )
    def _compute_lead_days(self):
        super()._compute_lead_days()
        # Override to use the orderpoint calendar to compute the 'lead_days_date'
        for orderpoint in self.with_context(bypass_delay_description=True):
            wh = orderpoint.warehouse_id
            if not orderpoint.product_id or not orderpoint.location_id:
                orderpoint.lead_days_date = False
                continue
            # Get the next planned date to execute this orderpoint
            start_date = orderpoint._get_next_reordering_date()
            # Get the lead days for this orderpoint
            lead_days = orderpoint._get_lead_days()
            # Get calendar, workday policy from warehouse
            calendar = wh.calendar_id
            policy = wh.orderpoint_on_workday and wh.orderpoint_on_workday_policy
            if calendar and policy == "skip_to_first_workday":
                # Consume all the lead days, then move up to the first workday
                # according to the calendar
                lead_days_date = calendar.plan_hours(
                    0, start_date + relativedelta(days=lead_days), compute_leaves=True
                )
            elif calendar and policy == "skip_all_non_workdays":
                # Postpone to the next available workday if needed, consuming lead days
                # only on workdays
                lead_days_date = calendar.plan_hours(0, start_date, compute_leaves=True)
                if lead_days_date.date() != start_date.date():
                    # We've consumed a lead day if the lead date is not the start date
                    lead_days -= 1
                while lead_days > 0:
                    # Always get the next working day according to the calendar, and
                    # decrease the lead days at each iteration
                    lead_days_date = calendar.plan_hours(
                        0, lead_days_date + relativedelta(days=1), compute_leaves=True
                    )
                    lead_days -= 1
            else:
                # Simply postpone according to delays
                lead_days_date = start_date + relativedelta(days=lead_days)
            orderpoint.lead_days_date = lead_days_date

    def _get_lead_days(self):
        self.ensure_one()
        lead_days, __ = self.rule_ids._get_lead_days(self.product_id)
        return lead_days

    def _get_next_reordering_date(self):
        self.ensure_one()
        now = fields.Datetime.now()
        calendar = self.warehouse_id.orderpoint_calendar_id
        # TODO: should we take into account days off or the reordering calendar with
        #  'compute_leaves=True' here?
        return calendar and calendar.plan_hours(0, now) or now

    @api.depends("rule_ids", "product_id.seller_ids", "product_id.seller_ids.delay")
    def _compute_json_popover(self):
        # Overridden to sent the OP ID to 'stock.rule._get_lead_days()'
        # method through the context, so we can display the reordering date
        # on the popover forecast widget
        for orderpoint in self:
            orderpoint = orderpoint.with_context(orderpoint_id=orderpoint.id)
            super(StockWarehouseOrderpoint, orderpoint)._compute_json_popover()
