# -*- coding: utf-8 -*-
#
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp.osv import orm, osv
from openerp.tools.translate import _


class FillInventoryWizard(orm.TransientModel):

    """If inventory as sub inventories,
       do not fill with sub inventories location"""
    _inherit = 'stock.fill.inventory'

    def fill_inventory(self, cr, uid, ids, context=None):
        """ To Import stock inventory according to products available in
            the location and not already in a sub inventory

        We split fill_inventory on many fill_inventory (one for each location)
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        if ids and len(ids):
            ids = ids[0]
        else:
            return {'type': 'ir.actions.act_window_close'}
        fill_inventory = self.browse(cr, uid, ids, context=context)
        if fill_inventory.recursive and fill_inventory.exhaustive:
            exclude_location_ids = []
            for i in self.pool['stock.inventory'].browse(
                    cr, uid, context['active_ids']):
                for sub_inventory in i.inventory_ids:
                    # exclude these location
                    exclude_location_ids.append(sub_inventory.location_id.id)
            domain = [
                ('location_id', 'child_of', [fill_inventory.location_id.id])]
            if exclude_location_ids:
                domain.append('!')
                domain.append(
                    ('location_id', 'child_of', exclude_location_ids))
            location_ids = self.pool['stock.location'].search(cr, uid, domain,
                                                              order="id",
                                                              context=context)
            all_in_exception = 0
            for location_id in location_ids:
                try:
                    super(FillInventoryWizard, self).fill_inventory(
                        cr, uid,
                        [self.copy(cr, uid, ids, {'location_id': location_id,
                                                  'recursive': False, },
                                   context=context)],
                        context=context)
                except osv.except_osv, e:
                    if e.value == _('No product in this location. Please '
                                    'select a location in the product form.'):
                        all_in_exception = all_in_exception + 1
                        pass
                    else:
                        raise e
            if all_in_exception == len(location_ids):
                raise osv.except_osv(_('Warning!'), _(
                    'No product in this location. Please select a location '
                    'in the product form.'))
            return {'type': 'ir.actions.act_window_close'}
        else:
            return super(FillInventoryWizard, self).fill_inventory(
                cr, uid, [ids], context=context)
