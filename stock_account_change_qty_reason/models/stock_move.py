# Copyright 2019-2024 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_accounting_data_for_valuation(self):
        self.ensure_one()
        (
            journal_id,
            acc_src,
            acc_dest,
            acc_valuation,
        ) = super()._get_accounting_data_for_valuation()
        preset_reason = self.move_line_ids.preset_reason_id
        if preset_reason:
            if preset_reason.account_reason_input_id:
                acc_src = preset_reason.account_reason_input_id.id
            if preset_reason.account_reason_output_id:
                acc_dest = preset_reason.account_reason_output_id.id
        return journal_id, acc_src, acc_dest, acc_valuation
