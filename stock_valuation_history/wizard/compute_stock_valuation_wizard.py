# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
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

from openerp.osv import osv, fields
from openerp.tools.translate import _


class compute_stock_valuation(osv.TransientModel):
    _name = "stock.valuation.history.wizard"
    _description = "Stock Valuation wizard"

    _columns = {
        'name': fields.char('Title', size=64),
        'location_id': fields.many2one(
            'stock.location', 'Location', required=True),
    }

    def action_ok(self, cr, uid, ids, context=None):
        """Call the computation module and open the result screen.

        A default name will be generated if none is given."""
        if context is None:
            context = {}

        wizard = self.browse(cr, uid, ids[0], context=context)

        context = context.copy()
        context['location'] = wizard.location_id.id
        if wizard.name:
            context['name'] = wizard.name

        valuation_ids = self.pool['product.product'].search_create_valuation(
            cr, uid, [('qty_available', '>', 0)], context=context)

        view_ids = self.pool['ir.model.data'].get_object_reference(
            cr, uid,
            'stock_valuation_history',
            'stock_valuation_history_tree_view')
        view_id = view_ids and view_ids[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Valuation'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_ids': [view_id],
            'res_model': 'stock.valuation.history',
            'context': {'search_default_group_by_name': 1,
                        'search_default_group_by_category': 1,
                        'search_default_group_by_uom': 1},
            'domain': [('id', 'in', valuation_ids)],
        } or True
