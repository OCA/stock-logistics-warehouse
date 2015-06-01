# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2013 Numérigraphe SARL. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp.tools.translate import _

from stock_inventory_hierarchical import HierarchicalInventoryException

# Add the date to the list of fields we must propagate to children inventories
from stock_inventory_hierarchical import PARENT_VALUES
PARENT_VALUES.append('exhaustive')


class HierarchicalExhInventory(orm.Model):
    """Add hierarchical structure features to exhaustive Inventories"""
    _inherit = 'stock.inventory'

    def action_open(self, cr, uid, ids, context=None):
        """Open only if all the parents are Open."""
        for inventory in self.browse(cr, uid, ids, context=context):
            while inventory.parent_id:
                inventory = inventory.parent_id
                if inventory.state != 'open':
                    raise HierarchicalInventoryException(
                        _('Warning'),
                        _('One of the parent inventories is not open.'))
        return super(HierarchicalExhInventory, self).action_open(
            cr, uid, ids, context=context)

    def get_missing_locations(self, cr, uid, ids, context=None):
        """Extend the list of inventories with their children"""
        ids = self.search(
            cr, uid, [('parent_id', 'child_of', ids)], context=context)
        missing_ids = super(
            HierarchicalExhInventory, self).get_missing_locations(
                cr, uid, ids, context=context)
        # Find the locations already included in sub-inventories
        inventories = self.browse(cr, uid, ids, context=context)
        subinv_location_ids = [sub.location_id.id
                               for i in inventories
                               for sub in i.inventory_ids]
        if not subinv_location_ids:
            return missing_ids
        # Extend to the children locations
        subinv_location_ids = set(self.pool['stock.location'].search(
            cr, uid, [
                ('location_id', 'child_of', subinv_location_ids),
                ('usage', '=', 'internal')], context=context))
        return list(set(missing_ids) - subinv_location_ids)

    # TODO v8: probably only keep the state "done"
    def confirm_missing_locations(self, cr, uid, ids, context=None):
        """Do something only if children state are confirm or done."""
        children_count = self.search(
            cr, uid, [('parent_id', 'child_of', ids),
                      ('id', 'not in', ids),
                      ('state', 'not in', ['confirm', 'done'])],
            context=context, count=True)
        if children_count > 0:
            raise HierarchicalInventoryException(
                _('Warning'),
                _('Some Sub-inventories are not confirmed.'))
        return super(HierarchicalExhInventory,
                     self).confirm_missing_locations(
            cr, uid, ids, context=context)

    def onchange_location_id(self, cr, uid, ids, location_id, context=None):
        """Check if location is a child of parent inventory location"""
        loc_obj = self.pool['stock.location']
        for inventory in self.browse(cr, uid, ids, context=context):
            if inventory.parent_id:
                allowed_location_ids = loc_obj.search(
                    cr, uid, [('location_id', 'child_of',
                               inventory.parent_id.location_id.id)],
                    context=context)
                if location_id not in allowed_location_ids:
                    return {
                        'location_id': False,
                        'warning': {
                            'title': _('Warning: Wrong location'),
                            'message': _("This location is not declared on "
                                         "the parent inventory\n"
                                         "It cannot be added.")}
                    }
        return {}
