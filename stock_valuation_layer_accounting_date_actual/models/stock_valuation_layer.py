# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    @api.depends(
        "create_date",
        "account_move_id.state",
        "account_move_id.date",
        "stock_move_id.actual_date",
        "stock_move_id.state",
    )
    def _compute_accounting_date(self):
        layers = self.filtered(lambda l: not l.account_move_id)
        for rec in layers:
            rec.accounting_date = rec.stock_move_id.actual_date
        return super(StockValuationLayer, self - layers)._compute_accounting_date()
