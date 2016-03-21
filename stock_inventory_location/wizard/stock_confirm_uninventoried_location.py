# -*- encoding: utf-8 -*-
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

from openerp.tools.translate import _
from openerp.osv import fields, orm, osv


class stock_inventory_uninventoried_location(orm.TransientModel):
    _name = 'stock.inventory.uninventoried.locations'
    _description = 'Confirm the uninventoried Locations.'

    _columns = {
        'location_ids': fields.many2many(
            'stock.location',
            'stock_inventory_uninventoried_location_rel',
            'location_id', 'wizard_id',
            'Uninventoried location', readonly=True),
    }

    def default_locations(self, cr, uid, context=None):
        """Initialize view with the list of uninventoried locations."""
        return self.pool['stock.inventory'].get_missing_locations(
            cr, uid, context['active_ids'], context=context)

    _defaults = {
        'location_ids': default_locations,
    }

    def confirm_uninventoried_locations(self, cr, uid, ids, context=None):
        """Add the missing inventory lines with qty=0 and confirm inventory"""
        inventory_ids = context['active_ids']
        inventory_obj = self.pool['stock.inventory']
        wizard_obj = self.pool['stock.fill.inventory']
        for inventory in inventory_obj.browse(cr, uid, inventory_ids,
                                              context=context):
            if inventory.exhaustive:
                # silently run the import wizard with qty=0
                try:
                    # on parent inventory it is possible that fill inventory
                    # fail with no product
                    wizard_id = wizard_obj.create(
                        cr, uid, {'location_id': inventory.location_id.id,
                                  'recursive': True,
                                  'set_stock_zero': True,
                                  'exhaustive': True}, context=context)
                    wizard_obj.fill_inventory(cr, uid, [wizard_id],
                                              context=context)
                except osv.except_osv, e:
                    if e.value == _('No product in this location. Please '
                                    'select a location in the product form.'):
                        pass

        inventory_obj.action_confirm(cr, uid, inventory_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}
