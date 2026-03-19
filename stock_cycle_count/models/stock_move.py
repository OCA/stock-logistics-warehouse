# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        # Use sudo() because the user triggering _action_done may not have
        # access to cycle count models (stock.cycle.count.rule, stock.cycle.count).
        self.mapped("location_id").sudo().check_zero_confirmation()
        return res
