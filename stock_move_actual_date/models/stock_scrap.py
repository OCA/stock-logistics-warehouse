# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockScrap(models.Model):
    _name = "stock.scrap"
    _inherit = ["stock.scrap", "actual.date.mixin"]

    def _get_stock_moves(self):
        self.ensure_one()
        return self.move_ids

    def do_scrap(self):
        for scrap in self:
            scrap = scrap.with_context(actual_date_source=scrap.actual_date)
            super(StockScrap, scrap).do_scrap()
        return True
