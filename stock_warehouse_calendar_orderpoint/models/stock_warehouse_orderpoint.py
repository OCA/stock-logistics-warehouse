# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)


from dateutil import relativedelta

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.depends(
        "rule_ids",
        "product_id.seller_ids",
        "product_id.seller_ids.delay",
        "warehouse_id.orderpoint_calendar_id",
    )
    def _compute_lead_days(self):
        super()._compute_lead_days()
        # Override to use the orderpoint calendar to compute the 'lead_days_date'
        for orderpoint in self.with_context(bypass_delay_description=True):
            op_calendar = orderpoint.warehouse_id.orderpoint_calendar_id
            if not op_calendar:
                continue
            if not orderpoint.product_id or not orderpoint.location_id:
                orderpoint.lead_days_date = False
                continue
            lead_days = orderpoint._get_lead_days()
            # Get the next planned date to execute this orderpoint
            start_date = orderpoint._get_next_reordering_date()
            lead_days_date = start_date + relativedelta.relativedelta(days=lead_days)
            # Postpone to the next available workday if needed
            calendar = orderpoint.warehouse_id.calendar_id
            if orderpoint.warehouse_id.orderpoint_on_workday and calendar:
                lead_days_date = calendar.plan_hours(
                    0, lead_days_date, compute_leaves=True
                )
            orderpoint.lead_days_date = lead_days_date

    def _get_lead_days(self):
        self.ensure_one()
        lead_days, __ = self.rule_ids._get_lead_days(self.product_id)
        return lead_days

    def _get_next_reordering_date(self):
        self.ensure_one()
        calendar = self.warehouse_id.orderpoint_calendar_id
        if calendar:
            # TODO: should we take into account days off or the reordering
            # calendar with 'compute_leaves=True' here?
            return calendar.plan_hours(0, fields.Datetime.now())
        return False

    @api.depends("rule_ids", "product_id.seller_ids", "product_id.seller_ids.delay")
    def _compute_json_popover(self):
        # Overridden to sent the OP ID to 'stock.rule._get_lead_days()'
        # method through the context, so we can display the reordering date
        # on the popover forecast widget
        for orderpoint in self:
            orderpoint = orderpoint.with_context(orderpoint_id=orderpoint.id)
            super(StockWarehouseOrderpoint, orderpoint)._compute_json_popover()
