# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from datetime import datetime


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom,
                               location_id, name, origin, values, group_id):
        res = super(ProcurementRule, self)._get_stock_move_values(
            product_id, product_qty, product_uom,
            location_id, name, origin, values, group_id)
        dt_planned = fields.Datetime.from_string(values['date_planned'])
        warehouse = self.propagate_warehouse_id or self.warehouse_id
        if warehouse.calendar_id and self.delay:
            date_expected = warehouse.calendar_id.plan_days(
                -1 * self.delay - 1, dt_planned)
            if date_expected > datetime.now():
                res['date'] = date_expected
                res['date_expected'] = date_expected
        return res
