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

from openerp.osv import fields, orm


class FillInventoryWizard(orm.TransientModel):
    """Add a field that lets the client make the location read-only"""
    _inherit = 'stock.fill.inventory'

    _columns = {
        'exhaustive': fields.boolean('Exhaustive', readonly=True)
    }

    def default_get(self, cr, uid, fields, context=None):
        """Get 'location_id' and 'exhaustive' from the inventory"""
        if context is None:
            context = {}
        inv_id = context.get('active_id')

        res = super(FillInventoryWizard, self).default_get(
            cr, uid, fields, context=context)
        if (context.get('active_model') == 'stock.inventory'
                and inv_id
                and 'location_id' in fields):
            inventory = self.pool['stock.inventory'].browse(
                cr, uid, context['active_id'], context=context)
            res.update({'location_id': inventory.location_id.id,
                        'exhaustive': inventory.exhaustive})
        return res
