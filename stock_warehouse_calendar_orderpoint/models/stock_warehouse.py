# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    orderpoint_calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Reordering Calendar",
        default=lambda o: o._default_orderpoint_calendar_id(),
        help="Calendar used to scheduled the execution of reordering rules",
    )
    orderpoint_on_workday = fields.Boolean(
        string="Reordering on Workday",
        default=lambda o: o._default_orderpoint_on_workday(),
        help=(
            "Postpone the lead date to the first available workday. "
            "This is based on the Working Hours calendar."
        ),
    )

    def _default_orderpoint_calendar_id(self):
        return self.env.company.orderpoint_calendar_id

    def _default_orderpoint_on_workday(self):
        return self.env.company.orderpoint_on_workday
