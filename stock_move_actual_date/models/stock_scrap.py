# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockScrap(models.Model):
    _name = "stock.scrap"
    _inherit = ["stock.scrap", "actual.date.mixin"]

    def write(self, vals):
        res = super().write(vals)
        if "actual_date" in vals:
            for rec in self:
                if rec.state != "done":
                    continue
                account_moves = rec.move_id.account_move_ids
                if not account_moves:
                    continue
                account_moves._update_accounting_date()
        return res

    def do_scrap(self):
        """Passes the actual_date as context to be used in _compute_actual_date()
        of stock move.
        """
        for scrap in self:
            scrap = scrap.with_context(actual_date=scrap.actual_date)
            super(StockScrap, scrap).do_scrap()
        return True
