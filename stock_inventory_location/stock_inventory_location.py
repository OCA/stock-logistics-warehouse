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

import time
from collections import Iterable

from openerp.osv import orm, fields
from openerp.tools.translate import _
# The next 2 imports are only needed for a feature backported from trunk-wms
# TODOv8! remove, feature is included upstream
from openerp.osv import osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID

from .exceptions import ExhaustiveInventoryException


class StockInventory(orm.Model):

    """Add locations to the inventories"""
    _inherit = 'stock.inventory'

    INVENTORY_STATE_SELECTION = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    _columns = {
        # TODO v8: should we use "confirm" instead of adding "open"?
        'state': fields.selection(
            INVENTORY_STATE_SELECTION, 'State', readonly=True, select=True),
        # TODO v8: remove this, should not be needed anymore
        # Make the inventory lines read-only in all states except "Open",
        # to ensure that no unwanted Location can be inserted
        'inventory_line_id': fields.one2many(
            'stock.inventory.line', 'inventory_id', 'Inventory lines',
            readonly=True, states={'open': [('readonly', False)]}),
        # TODO v8: remove this, it's backported from v8
        'location_id': fields.many2one(
            'stock.location', 'Inventoried Location',
            readonly=True, states={'draft': [('readonly', False)]}),
        'exhaustive': fields.boolean(
            'Exhaustive', readonly=True,
            states={'draft': [('readonly', False)]},
            help="Check the box if you are conducting an exhaustive "
                 "Inventory.\n"
                 "Leave the box unchecked if you are conducting a standard "
                 "Inventory (partial inventory for example).\n"
                 "For an exhaustive Inventory:\n"
                 " - the status \"Draft\" lets you define the list of "
                 "Locations where goods must be counted\n"
                 " - the status \"Open\" indicates that the list of Locations "
                 "is definitive and you are now counting the goods. In that "
                 "status, no Stock Moves can be recorded in/out of the "
                 "Inventory's Locations\n"
                 " - only the Inventory's Locations can be entered in the "
                 "Inventory Lines\n"
                 " - if some of the Inventory's Locations have not been "
                 "entered in the Inventory Lines, OpenERP warns you "
                 "when you confirm the Inventory\n"
                 " - every good that is not in the Inventory Lines is "
                 "considered lost, and gets moved out of the stock when you "
                 "confirm the Inventory"),
    }

    def action_open(self, cr, uid, ids, context=None):
        """Change the state of the inventory to 'open'"""
        return self.write(cr, uid, ids, {'state': 'open'}, context=context)

    # TODO v8: remove this method? the feature looks already done upstream
    def action_done(self, cr, uid, ids, context=None):
        """
        Don't allow to make an inventory with a date in the future.

        This makes sure no stock moves will be introduced between the
        moment you finish the inventory and the date of the Stock Moves.
        Backported from trunk-wms:
            revid:qdp-launchpad@openerp.com-20140317090656-o7lo22tzm8yuv3r8

        @raise osv.except_osv:
            We raise this exception on purpose instead of
            ExhaustiveInventoryException to ensure forward-compatibility
            with v8.
        """
        for inventory in self.browse(cr, uid, ids, context=None):
            if inventory.date > time.strftime(DEFAULT_SERVER_DATETIME_FORMAT):
                raise osv.except_osv(
                    _('Error!'),
                    _('It\'s impossible to confirm an inventory in the '
                      'future. Please change the inventory date to proceed '
                      'further.'))
        return super(StockInventory, self).action_done(cr, uid, ids,
                                                       context=context)

    # TODO: remove this in v8
    def _default_location(self, cr, uid, ids, context=None):
        """Default stock location

        @return: id of the stock location of the first warehouse of the
        default company"""
        location_id = False
        company_id = self.pool['res.company']._company_default_get(
            cr, uid, 'stock.warehouse', context=context)
        warehouse_id = self.pool['stock.warehouse'].search(
            cr, uid, [('company_id', '=', company_id)], limit=1)
        if warehouse_id:
            location_id = self.pool['stock.warehouse'].read(
                cr, uid, warehouse_id[0], ['lot_stock_id'])['lot_stock_id'][0]
        return location_id

    _defaults = {
        'state': 'draft',
        'exhaustive': False,
        # TODO: remove this in v8
        'location_id': _default_location,
    }

    def _check_location_free_from_inventories(self, cr, uid, ids):
        """
        Verify that no other Inventory is being conducted on the same locations

        Open Inventories are matched using the exact Location IDs,
        excluding children.
        """
        # We don't get a context because we're called from a _constraint
        for inventory in self.browse(cr, uid, ids):
            if not inventory.exhaustive:
                # never block standard inventories
                continue
            if self.search(cr, uid,
                           [('location_id', '=', inventory.location_id.id),
                            ('id', '!=', inventory.id),
                            ('date', '=', inventory.date),
                            ('exhaustive', '=', True)]):
                # Quit as soon as one offending inventory is found
                return False
        return True

    _constraints = [
        (_check_location_free_from_inventories,
         'Other Physical inventories are being conducted using the same '
         'Locations.',
         ['location_id', 'date', 'exhaustive'])
    ]

    def _get_locations_open_inventories(self, cr, uid, context=None):
        """IDs of location in open exhaustive inventories, with children"""
        inv_ids = self.search(
            cr, uid, [('state', '=', 'open'), ('exhaustive', '=', True)],
            context=context)
        if not inv_ids:
            # Early exit if no match found
            return []
        # List the Locations - normally all exhaustive inventories have one
        location_ids = [inventory.location_id.id
                        for inventory in self.browse(cr, uid, inv_ids,
                                                     context=context)]
        # Extend to the children Locations
        return self.pool['stock.location'].search(
            cr, uid,
            [('location_id', 'child_of', set(location_ids)),
             ('usage', '=', 'internal')],
            context=context)

    def get_missing_locations(self, cr, uid, ids, context=None):
        """Compute the list of location_ids which are missing from the lines

        Here, "missing" means the location is the inventory's location or one
        of it's children, and the inventory does not contain any line with
        this location."""
        inventories = self.browse(cr, uid, ids, context=context)
        # Find the locations of the inventories
        inv_location_ids = [i.location_id.id for i in inventories]
        # Extend to the children locations
        inv_location_ids = set(self.pool['stock.location'].search(
            cr, uid, [
                ('location_id', 'child_of', inv_location_ids),
                ('usage', '=', 'internal')], context=context))
        # Find the locations already recorded in inventory lines
        line_locations_ids = set([l.location_id.id
                                  for i in inventories
                                  for l in i.inventory_line_id])
        return list(inv_location_ids - line_locations_ids)

    def confirm_missing_locations(self, cr, uid, ids, context=None):
        """Open wizard to confirm empty locations on exhaustive inventories"""
        for inventory in self.browse(cr, uid, ids, context=context):
            if (self.get_missing_locations(cr, uid, ids, context=context)
                    and inventory.exhaustive):
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.inventory.uninventoried.locations',
                    'target': 'new',
                    'context': dict(context,
                                    active_ids=ids,
                                    active_id=ids[0]),
                    'nodestroy': True,
                }
        return self.action_confirm(cr, uid, ids, context=context)


class StockInventoryLine(orm.Model):

    """Only allow the Inventory's Locations"""

    _inherit = 'stock.inventory.line'

    def _default_stock_location(self, cr, uid, context=None):
        res = super(StockInventoryLine, self)._default_stock_location(
            cr, uid, context=context)
        if context is None or not context.get('location_id', False):
            return res
        else:
            return context['location_id']

    _defaults = {
        'location_id': _default_stock_location
    }

    def onchange_location_id(self, cr, uid, ids, inventory_location_id,
                             exhaustive, location_id, context=None):
        """Warn if the new is not in the location list for this inventory."""
        if not exhaustive:
            # Don't check if partial inventory
            return True

        # search children of location
        if location_id not in self.pool['stock.location'].search(
                cr, uid, [('location_id', 'child_of', inventory_location_id)],
                context=context):
            return {
                'value': {'location_id': False},
                'warning': {
                    'title': _('Warning: Wrong location'),
                    'message': _(
                        "You cannot record an Inventory Line for this "
                        "Location.\n"
                        "You must first add this Location to the list of "
                        "affected Locations on the Inventory form.")}
            }
        return True


class StockLocation(orm.Model):

    """Refuse changes during exhaustive Inventories"""
    _inherit = 'stock.location'
    _order = 'name'

    def _check_inventory(self, cr, uid, ids, context=None):
        """Error if an exhaustive Inventory is being conducted here"""
        inv_obj = self.pool['stock.inventory']
        location_inventory_open_ids = inv_obj._get_locations_open_inventories(
            cr, SUPERUSER_ID, context=context)
        if not isinstance(ids, Iterable):
            ids = [ids]
        for inv_id in ids:
            if inv_id in location_inventory_open_ids:
                raise ExhaustiveInventoryException(
                    _('Error: Location locked down'),
                    _('A Physical Inventory is being conducted at this '
                      'location'))
        return True

    def write(self, cr, uid, ids, vals, context=None):
        """Refuse write if an inventory is being conducted"""
        self._check_inventory(cr, uid, ids, context=context)
        if not isinstance(ids, Iterable):
            ids_to_check = [ids]
        else:
            # Copy the data to avoid changing 'ids',
            # it would trigger an infinite recursion
            ids_to_check = list(ids)
        # If changing the parent, no inventory must conducted there either
        if vals.get('location_id'):
            ids_to_check.append(vals['location_id'])
        self._check_inventory(cr, uid, ids_to_check, context=context)
        return super(StockLocation, self).write(cr, uid, ids, vals,
                                                context=context)

    def create(self, cr, uid, vals, context=None):
        """Refuse create if an inventory is being conducted at the parent"""
        self._check_inventory(cr, uid, vals.get('location_id'),
                              context=context)
        return super(StockLocation, self).create(cr, uid, vals,
                                                 context=context)

    def unlink(self, cr, uid, ids, context=None):
        """Refuse unlink if an inventory is being conducted"""
        self._check_inventory(cr, uid, ids, context=context)
        return super(StockLocation, self).unlink(cr, uid, ids, context=context)


class StockMove(orm.Model):

    """Refuse Moves during exhaustive Inventories"""

    _inherit = 'stock.move'

    # TODOv7: adapt this to match trunk-wms
    def _check_open_inventory_location(self, cr, uid, ids, context=None):
        """
        Check that the locations are not locked by an open inventory

        Standard inventories are not checked.

        @raise ExhaustiveInventoryException: an error is raised if locations
            are locked, instead of returning False, in order to pass an
            extensive error message back to users.
        """
        message = ""
        inv_obj = self.pool['stock.inventory']
        locked_location_ids = inv_obj._get_locations_open_inventories(
            cr, SUPERUSER_ID, context=context)
        if not locked_location_ids:
            # Nothing to verify
            return True
        for move in self.browse(cr, uid, ids, context=context):
            if (move.location_id.usage != 'inventory'
                    and move.location_dest_id.id in locked_location_ids):
                message += " - %s\n" % (move.location_dest_id.name)
            if (move.location_dest_id.usage != 'inventory'
                    and move.location_id.id in locked_location_ids):
                message += " - %s\n" % (move.location_id.name)
        if message:
            raise ExhaustiveInventoryException(
                _('Error: Location locked down'),
                _('A Physical Inventory is being conducted at the following '
                  'location(s):\n%s') % message)
        return True

    _constraints = [
        (_check_open_inventory_location,
         "A Physical Inventory is being conducted at this location",
         ['location_id', 'location_dest_id']),
    ]
