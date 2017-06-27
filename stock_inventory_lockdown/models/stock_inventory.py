# -*- coding: utf-8 -*-
# © 2013-2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def _get_locations_open_inventories(self, locations_ids=None):
        """IDs of locations in open exhaustive inventories, with children"""
        inventory_domain = [('state', '=', 'confirm')]
        if locations_ids:
            inventory_domain.append(('location_id', 'child_of', locations_ids))
        inventories = self.search(inventory_domain)
        if not inventories:
            # Early exit if no match found
            return []
        location_ids = inventories.mapped('location_id')

        # Extend to the children Locations
        location_domain = [
            ('location_id', 'child_of', location_ids.ids),
            ('usage', 'in', ['internal', 'transit'])]
        if locations_ids:
            location_domain.append(('location_id', 'child_of', locations_ids))
        return self.env['stock.location'].search(location_domain)
