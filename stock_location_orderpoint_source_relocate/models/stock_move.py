# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        self = self.with_context(skip_auto_replenishment=True)
        super()._action_assign()

    def _apply_source_relocate(self):
        res = super()._apply_source_relocate()
        res = res.with_context(skip_auto_replenishment=False)
        res._prepare_auto_replenishment_for_waiting_moves()
        return res
