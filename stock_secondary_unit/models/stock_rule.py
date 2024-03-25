# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _run_pull(self, procurements):
        self = self.with_context(avoid_accumulate_secondary_uom_qty=True)
        return super()._run_pull(procurements)
