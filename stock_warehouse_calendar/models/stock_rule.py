# Copyright 2018-19 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models
from datetime import datetime


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom,
                               location_id, name, origin, values, group_id):
        res = super(StockRule, self)._get_stock_move_values(
            product_id, product_qty, product_uom,
            location_id, name, origin, values, group_id)
        warehouse = self.propagate_warehouse_id or self.warehouse_id
        if warehouse.calendar_id and self.delay:
            date_expected = warehouse.wh_plan_days(
                values['date_planned'], -1 * self.delay)
            if date_expected > datetime.now():
                res['date'] = date_expected
                res['date_expected'] = date_expected
        return res
