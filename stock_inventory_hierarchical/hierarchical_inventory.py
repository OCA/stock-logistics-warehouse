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

from openerp.osv import orm, fields
from openerp.tools.translate import _

from .exceptions import HierarchicalInventoryException

# Add the date to the list of fields we must propagate to children inventories
from . import PARENT_VALUES
PARENT_VALUES.append('date')


class HierarchicalInventory(orm.Model):
    _inherit = 'stock.inventory'

    _parent_store = True
    _parent_order = 'date, name'
    _order = 'parent_left'

    def name_get(self, cr, uid, ids, context=None):
        """Show the parent inventory's name in the name of the children

        :param dict context: the ``inventory_display`` key can be
                             used to select the short version of the
                             inventory name (without the direct parent),
                             when set to ``'short'``. The default is
                             the long version."""
        if context is None:
            context = {}
        if context.get('inventory_display') == 'short':
            # Short name context: just do the usual stuff
            return super(HierarchicalInventory, self).name_get(
                cr, uid, ids, context=context)
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    def name_search(self, cr, uid, name='', args=None, operator='ilike',
                    context=None, limit=100):
        """Enable search on value returned by name_get ("parent / child")"""
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            # Make sure name_search is symmetric to name_get
            name = name.split(' / ')[-1]
            ids = self.search(cr, uid, [('name', operator, name)] + args,
                              limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context=context)

    def _complete_name(self, cr, uid, ids, field_name, arg, context=None):
        """Function-field wrapper to get the complete name from name_get"""
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _progress_rate(self, cr, uid, ids, field_name, arg, context=None):
        """Rate of (sub)inventories done/total"""
        rates = {}
        for current_id in ids:
            nb = self.search(
                cr, uid, [('parent_id', 'child_of', current_id)],
                context=context, count=True)
            if not nb:
                # No inventory, consider it's 0% done
                rates[current_id] = 0
                continue
            nb_done = self.search(
                cr, uid, [('parent_id', 'child_of', current_id),
                          ('state', '=', 'done')],
                context=context, count=True)
            rates[current_id] = 100 * nb_done / nb
        return rates

    _columns = {
        # name_get() only changes the default name of the record, not the
        # content of the field "name" so we add another field for that
        'complete_name': fields.function(
            _complete_name, type="char",
            string='Complete reference'),
        'parent_id': fields.many2one(
            'stock.inventory', 'Parent Inventory', ondelete='cascade',
            readonly=True, states={'draft': [('readonly', False)]}),
        'inventory_ids': fields.one2many(
            'stock.inventory', 'parent_id', 'List of Sub-inventories',
            readonly=True, states={'draft': [('readonly', False)]}),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
        'progress_rate': fields.function(
            _progress_rate, string='Progress', type='float'),
        }

    _constraints = [
        (orm.Model._check_recursion,
         'Error: You can not create recursive inventories.',
         ['parent_id']),
    ]

    def create(self, cr, uid, vals, context=None):
        """Copy selected values from parent to child"""
        if vals and vals.get('parent_id'):
            existing_fields = self.fields_get_keys(cr, uid, context=context)
            parent_values = self.read(cr, uid, [vals['parent_id']],
                                      PARENT_VALUES, context=context)
            vals = vals.copy()
            vals.update({field: parent_values[0][field]
                         for field in PARENT_VALUES
                         if field in existing_fields})
        return super(HierarchicalInventory, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """Copy selected values from parent to children"""
        if context is None:
            context = {}

        values = super(HierarchicalInventory, self).write(
            cr, uid, ids, vals, context=context)
        if not vals or context.get('norecurse', False):
            return values

        # filter the fields we want to propagate
        children_values = {
            field: vals[field] for field in PARENT_VALUES if field in vals
        }
        if not children_values:
            return values

        if not isinstance(ids, list):
            ids = [ids]
        # The context disables recursion - children are already included
        return self.write(
            cr, uid, self.search(cr, uid, [('parent_id', 'child_of', ids)]),
            children_values, context=dict(context, norecurse=True))

    def action_cancel_inventory(self, cr, uid, ids, context=None):
        """Cancel inventory only if all the parents are canceled"""
        inventories = self.browse(cr, uid, ids, context=context)
        for inventory in inventories:
            while inventory.parent_id:
                inventory = inventory.parent_id
                if inventory.state != 'cancel':
                    raise HierarchicalInventoryException(
                        _('Warning'),
                        _('One of the parent Inventories is not canceled.'))
        return super(HierarchicalInventory,
                     self).action_cancel_inventory(cr, uid, ids,
                                                   context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        """Confirm inventory only if all the children are confirmed"""
        children_count = self.search(
            cr, uid, [('parent_id', 'child_of', ids),
                      ('state', 'not in', ['confirm', 'done'])],
            context=context, count=True)
        if children_count > 1:
            raise HierarchicalInventoryException(
                _('Warning'),
                _('Some Sub-inventories are not confirmed.'))
        return super(HierarchicalInventory, self).action_confirm(
            cr, uid, ids, context=context)

    def action_done(self, cr, uid, ids, context=None):
        """Perform validation only if all the children states are 'done'."""
        children_count = self.search(cr, uid, [('parent_id', 'child_of', ids),
                                               ('state', '!=', 'done')],
                                     context=context, count=True)
        if children_count > 1:
            raise HierarchicalInventoryException(
                _('Warning'),
                _('Some Sub-inventories are not validated.'))
        return super(HierarchicalInventory, self).action_done(
            cr, uid, ids, context=context)
