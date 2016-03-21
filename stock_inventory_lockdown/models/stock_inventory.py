# -*- coding: utf-8 -*-
# © 2013-2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def _get_locations_open_inventories(self):
        """IDs of location in open exhaustive inventories, with children"""
        inventories = self.search([('state', '=', 'confirm')])
        if not inventories:
            # Early exit if no match found
            return []
        location_ids = inventories.mapped('location_id')

        # Extend to the children Locations
        return self.env['stock.location'].search(
            [('location_id', 'child_of', location_ids.ids),
             ('usage', 'in', ['internal', 'transit'])])

    @api.multi
    def action_done(self):
        """Add value in the context to ignore the lockdown"""
        return super(StockInventory,
                     self.with_context(bypass_lockdown=True)).action_done()
