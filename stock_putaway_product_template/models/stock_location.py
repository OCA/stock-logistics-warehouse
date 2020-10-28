# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Tecnativa - Sergio Teruel

from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def _get_putaway_strategy(self, product):
        return super(
            StockLocation, self.with_context(filter_putaway_rule=True)
        )._get_putaway_strategy(product)
