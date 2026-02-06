# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.depends(
        "rule_ids",
        "product_id.seller_ids",
        "product_id.seller_ids.delay",
        "warehouse_id.calendar_id",
        "warehouse_id.orderpoint_calendar_id",
        "warehouse_id.orderpoint_on_workday_policy",
    )
    def _compute_lead_days(self):
        super()._compute_lead_days()
        # Override to use the WH/OP calendars to compute ``lead_days_date``
        for orderpoint in self.with_context(bypass_delay_description=True):
            if not orderpoint.product_id or not orderpoint.location_id:
                orderpoint.lead_days_date = False
                continue
            wh = orderpoint.warehouse_id
            # Get the lead days for this orderpoint
            lead_days = orderpoint._get_lead_days()
            # Get the reordering date from the OP calendar
            reordering_date = wh._get_next_reordering_date()
            # Compute the lead_days_date, according to the calendar
            orderpoint.lead_days_date = wh._get_lead_date(reordering_date, lead_days)

    def _get_lead_days(self):
        self.ensure_one()
        lead_days, __ = self.rule_ids._get_lead_days(self.product_id)
        return lead_days

    # DEPRECATED
    def _get_next_reordering_date(self):
        self.ensure_one()
        return self.warehouse_id._get_next_reordering_date()

    @api.depends("rule_ids", "product_id.seller_ids", "product_id.seller_ids.delay")
    def _compute_json_popover(self):
        # Overridden to send the OP ID to 'stock.rule._get_lead_days()'
        # method through the context, so we can display the reordering date
        # on the popover forecast widget
        for orderpoint in self:
            orderpoint = orderpoint.with_context(orderpoint_id=orderpoint.id)
            super(StockWarehouseOrderpoint, orderpoint)._compute_json_popover()
