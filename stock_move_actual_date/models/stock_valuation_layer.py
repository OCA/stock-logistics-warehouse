# Copyright 2025 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    actual_date = fields.Date(
        compute="_compute_actual_date",
        store=True,
        help=(
            "The actual date is determined as follows:\n"
            "- If a posted journal entry exists, its date is used.\n"
            "- If there is no journal entry, the stock move's actual date is used.\n"
            "- Otherwise, the record's creation date (timezone-aware) is used."
        ),
    )

    @api.depends(
        "create_date",
        "account_move_id.state",
        "account_move_id.date",
        "stock_move_id.actual_date",
        "stock_move_id.state",
    )
    def _compute_actual_date(self):
        for rec in self:
            account_move = rec.account_move_id
            if account_move and account_move.state == "posted":
                rec.actual_date = account_move.date
                continue
            if rec.stock_move_id.actual_date:
                rec.actual_date = rec.stock_move_id.actual_date
                continue
            rec.actual_date = fields.Datetime.context_timestamp(self, rec.create_date)
