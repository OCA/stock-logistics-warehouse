# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self, *args, **kwargs):
        self = self.with_context(skip_auto_replenishment=True)
        res = super()._action_assign(*args, **kwargs)
        self = self.with_context(skip_auto_replenishment=False)
        return res

    def _apply_source_relocate_rule(self, *args, **kwargs):
        relocated = super()._apply_source_relocate_rule(*args, **kwargs)
        if not relocated:
            return relocated
        relocated.with_context(
            skip_auto_replenishment=False
        )._prepare_auto_replenishment_for_waiting_moves()
        return relocated
