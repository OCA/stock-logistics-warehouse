# Copyright 2024 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def _action_done(self):
        super()._action_done()
        for inventory in self:
            done_locations = inventory._get_all_inventory_locations()
            last_inventory_date = inventory.date
            done_locations.write({"last_inventory_date": last_inventory_date})

    def _get_all_inventory_locations(self):
        """Return all locations that should be updated with the inventory date."""
        line_locations = self.line_ids.location_id
        if self.product_ids:
            return line_locations
        LOCATION = self.env["stock.location"]
        locations = LOCATION.search(
            [
                ("location_id", "child_of", self.location_ids.ids),
                ("usage", "in", ("internal", "transit")),
            ]
        )
        return LOCATION.browse(list(set(locations.ids) | set(line_locations.ids)))
