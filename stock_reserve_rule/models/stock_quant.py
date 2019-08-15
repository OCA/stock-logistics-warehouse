# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _group_by_location(self):
        """Return quants grouped by locations

        Group by location, but keeping the order of the quants (if we have more
        than one quant per location, the order is based on the first quant seen
        in the location). Thus, it can be used on a recordset returned by
        _gather.

        The returned format is: [(location, quants)]

        """
        quants_per_location = []
        seen = {}
        for quant in self:
            location = quant.location_id
            if location in seen:
                index = seen[location]
                quants_per_location[index][1] += quant
            else:
                quants_per_location.append((location, quant))
                seen[location] = len(quants_per_location) - 1
        return quants_per_location
