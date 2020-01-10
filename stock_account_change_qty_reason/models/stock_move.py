# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_accounting_data_for_valuation(self):
        self.ensure_one()
        journal_id, acc_src, acc_dest, acc_valuation = super(
            StockMove, self
        )._get_accounting_data_for_valuation()
        if self.preset_reason_id:
            if self.preset_reason_id.account_reason_input_id:
                acc_src = self.preset_reason_id.account_reason_input_id.id
            if self.preset_reason_id.account_reason_output_id:
                acc_dest = self.preset_reason_id.account_reason_output_id.id
        return journal_id, acc_src, acc_dest, acc_valuation
