import json

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_distribution = fields.Json(
        help="Distribution copied from the parent Stock Request",
    )

    def _prepare_account_move_line(
        self, qty, cost, credit_account_id, debit_account_id
    ):
        aml_vals = super()._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id
        )
        dist = self._get_clean_distribution()
        for line_vals in aml_vals:
            line_vals["analytic_distribution"] = dist
        return aml_vals

    def _get_clean_distribution(self):
        dist = self.analytic_distribution or {}
        if isinstance(dist, str):
            try:
                dist = json.loads(dist)
            except Exception:
                dist = {}
        return dist
