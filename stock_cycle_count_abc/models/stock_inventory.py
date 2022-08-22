# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def _allow_write(self, vals):
        if self.cycle_count_id.cycle_count_rule_id.rule_type == "abc":
            return False
        return super()._allow_write(vals)
