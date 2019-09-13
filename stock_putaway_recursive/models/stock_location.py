# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockLocation(models.Model):

    _inherit = 'stock.location'

    def get_putaway_strategy(self, product):
        if not self:
            # stop recursion
            return self
        current_location = super().get_putaway_strategy(product)
        next_location = current_location.get_putaway_strategy(product)
        return next_location or current_location
