# © 2013-2016 Numérigraphe SARL
# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def _get_locations_open_inventories(self, locations_ids=None):
        if not locations_ids:
            return []
        inventory_domain_same_location = [
            ("state", "=", "in_progress"),
            ("location_ids", "in", locations_ids),
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
                    location_id in location.child_internal_location_ids.ids
                    for location_id in locations_ids
                ):
                    inventories_parent |= inventory
        inventories = inventories_same_location | inventories_parent
        if not inventories:
            # Early exit if no match found
            return []
        location_ids = inventories.mapped("location_ids")
        location_domain = [
            ("id", "in", location_ids.ids),
            ("usage", "in", ["internal", "transit"]),
        ]
        return self.env["stock.location"].search(location_domain)
