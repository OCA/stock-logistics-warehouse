# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    def _quant_tasks(self):
        # Introduce a parameter that enable to run the
        # function even if disabled in company settings
        if self.env.company.defer_quant_tasks and not self.env.context.get(
            "run_defer_quant_tasks"
        ):
            return
        return super()._quant_tasks()

    @api.model
    def _quant_tasks_deferred(self):
        self.with_context(run_defer_quant_tasks=True)._quant_tasks()

    @api.model
    def _run_quant_tasks_deferred(self):
        self.with_delay(description="Executing Quant Tasks")._quant_tasks_deferred()
