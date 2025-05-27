# Copyright 2025 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def _get_open_inventories_by_locations(self, location_ids=None):
        if not location_ids:
            return self.env["stock.inventory"]

        inventory_domain_same_location = [
            ("state", "=", "in_progress"),
            ("location_ids", "in", location_ids),
        ]
        inventories_same_location = self.search(inventory_domain_same_location)

        inventory_domain_parent = [
            ("state", "=", "in_progress"),
            ("exclude_sublocation", "=", False),
        ]
        inventories_possible_parent = self.search(inventory_domain_parent)
        inventories_parent = self.env["stock.inventory"]

        for inventory in inventories_possible_parent:
            for location in inventory.location_ids:
                if any(
                    loc_id in location.child_internal_location_ids.ids
                    for loc_id in location_ids
                ):
                    inventories_parent |= inventory

        return inventories_same_location | inventories_parent
