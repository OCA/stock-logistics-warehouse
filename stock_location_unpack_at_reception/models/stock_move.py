# Copyright 2026 Camptocamp SA
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from collections import defaultdict

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_available_move_lines_in(self):
        # OVERRIDE: a chained move reserves exactly what its origin moves
        # brought, package included. What they brought into a location to
        # unpack at reception is no longer in that package: reserve it loose.
        # A package still there (e.g. it arrived before the location was set
        # to unpack) keeps its content: reserve it in the package.
        res = defaultdict(float)
        no_package = self.env["stock.package"]
        for key, quantity in super()._get_available_move_lines_in().items():
            location, lot, package, owner = key
            if location.unpack_at_reception and package.location_id != location:
                key = (location, lot, no_package, owner)
            res[key] += quantity
        return dict(res)
