# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def action_reset_quantity(self):
        self.filtered(
            lambda m: m.state in ("partially_available", "assigned")
        ).quantity = 0
