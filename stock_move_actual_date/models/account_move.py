# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _must_check_constrains_date_sequence(self):
        if self.env.context.get("skip_date_sequence_check"):
            return False
        return super()._must_check_constrains_date_sequence()

    def _update_accounting_date(self):
        self.button_draft()
        for move in self:
            move = move.with_context(skip_date_sequence_check=True)
            move.date = move.stock_move_id.actual_date
            if not move._sequence_matches_date():
                move.name = False
        self.action_post()
