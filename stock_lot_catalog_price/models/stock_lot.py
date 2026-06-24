# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockLot(models.Model):
    _inherit = "stock.lot"

    def _get_lst_price(self):
        return self.lst_price
