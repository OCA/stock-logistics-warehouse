# -*- coding: utf-8 -*-
# © 2013-2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api
from openerp.tools.translate import _

from openerp.exceptions import ValidationError


class StockInventory(models.Model):
    """Add hierarchical structure features to exhaustive Inventories"""
    _inherit = 'stock.inventory'

    @api.onchange('parent_id')
    def onchange_exhaustive(self):
        """Get the parent's value for `exhaustive`

        Use case: changing the parent of a sub-inventory"""
        # Only change if parent_id is set
        if self.parent_id:
            self.exhaustive = self.parent_id.exhaustive

    @api.multi
    def write(self, vals):
        """Propagate `exhaustive` from parent to children

        Use case: updating a parent inventory"""
        result = super(StockInventory, self).write(vals)
        if not vals:
            vals = {}
        # We must enforce `exhaustive` even if it's False => "not in vals"
        if ('exhaustive' not in vals or
                self.env.context.get('norecurse', False)):
            return result

        # Update all children at once, avoids recursive calls & DB round-trips
        children = self.search([('parent_id', 'child_of', self.ids)])
        return children.with_context(norecurse=True).write(
            {'exhaustive': vals['exhaustive']})

    def _get_default_exhaustive(self):
        """Exhaustive if parent is exhaustive or context demands it

        Use case: creating a new sub-inventory for an existing parent"""
        return (self.parent_id.exhaustive or
                self.env.context.get('force_exhaustive', False))

    @api.multi
    def _sub_inventory_locations(self):
        """Return the locations already included in sub-inventories"""
        inventories = self.search([('parent_id', 'child_of', self.ids)])

        # Don't warn if the locations already included in sub-inventories:
        # There was already a warning when the sub-inventory was done
        subinv_locations = inventories.mapped('inventory_ids.location_id')
        # Extend to the children locations
        return self.env['stock.location'].search(
            [('location_id', 'child_of', subinv_locations.ids),
             ('usage', 'in', ['internal', 'transit'])])

    @api.multi
    def get_missing_locations(self):
        """Do not warn about locations included in sub-inventories

        There has already been a warning when the sub-inventories were done"""
        locations = super(StockInventory, self).get_missing_locations()
        sub_inventory_locations = self._sub_inventory_locations()
        if sub_inventory_locations:
            return locations - sub_inventory_locations
        else:
            return locations

    @api.multi
    def confirm_missing_locations(self):
        """Do something only if children state are confirm or done.

        We could let the normal process run and fail but it's nicer to get
        a warning before, especially if the computation is long."""
        children_count = self.search_count(
            [('parent_id', 'child_of', self.ids),
             ('id', 'not in', self.ids),
             ('state', '!=', 'done')])
        if children_count > 0:
            raise ValidationError(
                _('Some sub-inventories are not done.'))
        return super(StockInventory, self).confirm_missing_locations()

    @api.multi
    def _inventory_locations_to_purge(self):
        """Don't add lines with qty=0 for locations of sub-inventories

        They have already been added when the sub-inventory was done"""
        locations = super(StockInventory, self)._inventory_locations_to_purge()
        sub_inventory_locations = self._sub_inventory_locations()
        if sub_inventory_locations:
            return locations - sub_inventory_locations
        else:
            return locations
