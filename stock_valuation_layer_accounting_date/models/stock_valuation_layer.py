# Copyright 2022 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    accounting_date = fields.Date(
        compute="_compute_accounting_date",
        store=True,
        help="Date of the linked journal entry if applicable, otherwise the create "
        "date of the record (timezone aware)",
    )

    @api.depends("create_date", "account_move_id.state", "account_move_id.date")
    def _compute_accounting_date(self):
        for rec in self:
            account_move = rec.account_move_id
            if account_move and account_move.state == "posted":
                rec.accounting_date = account_move.date
                continue
            rec.accounting_date = fields.Datetime.context_timestamp(
                self, rec.create_date
            )
