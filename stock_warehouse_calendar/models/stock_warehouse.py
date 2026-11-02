# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    calendar_id = fields.Many2one(
        comodel_name="resource.calendar", string="Working Hours", check_company=True
    )
    calendar_compute_leaves = fields.Boolean(
        string="Consider Global Time Off",
        help="Take into account the Global Time Off defined in the warehouse "
        "working hours (public holidays, plant shutdowns, ...) when planning "
        "warehouse operations.\n"
        "If not set, only the weekly working days are considered and those "
        "days are planned as if the warehouse were open.",
    )

    def wh_plan_days(self, date_from, delta):
        """Helper method to schedule warehouse operations based on its
        working days (if set).

        :param datetime date_from: reference date.
        :param integer delta: offset to apply.
        :return: datetime: resulting date.
        """
        self.ensure_one()
        if isinstance(delta, float):
            delta = round(delta)
        if not isinstance(date_from, datetime):
            date_from = fields.Datetime.to_datetime(date_from)
        if delta == 0:
            return date_from

        if self.calendar_id:
            if delta < 0:
                # We force the date planned to be at the beginning of the day.
                # So no work intervals are found in the reference date.
                dt_planned = date_from.replace(hour=0)
            else:
                # We force the date planned at the end of the day.
                dt_planned = date_from.replace(hour=23)
            date_result = self.calendar_id.plan_days(
                delta, dt_planned, compute_leaves=self.calendar_compute_leaves
            )
        else:
            date_result = date_from + timedelta(days=delta)
        return date_result
