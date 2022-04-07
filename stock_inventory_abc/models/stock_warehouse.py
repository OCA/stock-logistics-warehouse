# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    def _search_cycle_count_locations(self, rule):
        res = super()._search_cycle_count_locations(rule)
        if rule.apply_in == "warehouse" and rule.rule_type == "abc":
            return self.lot_stock_id
        if rule.apply_in == "location" and rule.rule_type == "abc":
            return rule.location_ids
        return res
