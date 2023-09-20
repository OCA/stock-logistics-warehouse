# © 2013-2016 Numérigraphe SARL
# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def _get_locations_open_inventories(self, locations_ids=None):
        """IDs of locations in open exhaustive inventories, with children"""
        inventory_domain = [("state", "=", "in_progress")]
        if locations_ids:
            inventory_domain.append(("location_ids", "child_of", locations_ids))
        inventories = self.search(inventory_domain)
        if not inventories:
            # Early exit if no match found
            return []
        location_ids = inventories.mapped("location_ids")

        # Extend to the children Locations
        location_domain = [
            "|",
            ("location_id", "in", location_ids.ids),
            ("location_id", "child_of", location_ids.ids),
            ("usage", "in", ["internal", "transit"]),
        ]
        return self.env["stock.location"].search(location_domain)
