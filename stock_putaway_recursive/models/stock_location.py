# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockLocation(models.Model):

    _inherit = 'stock.location'

    def get_putaway_strategy(self, product):
        loc = super().get_putaway_strategy(product)
        if loc != self:
            recursive_locations = self.env.context.get(
                '_recursive_locations', []
            )
            # avoid infinite recursion if putaway was already applied on loc
            if loc.id in recursive_locations:
                return self
            recursive_locations.append(loc.id)
            # apply putaway recursively
            return loc.with_context(
                _recursive_locations=recursive_locations
            ).get_putaway_strategy(product)
        return loc
