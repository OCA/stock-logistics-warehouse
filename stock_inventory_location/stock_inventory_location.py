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
            if (self.get_missing_locations(cr, uid, ids, context=context) and
                    inventory.exhaustive):
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
