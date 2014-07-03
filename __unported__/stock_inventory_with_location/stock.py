# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

from osv import fields, osv
from tools.translate import _

class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    
    _columns = {
    }
    
    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirm the inventory and writes its finished date
        @return: True
        """
        res = super(stock_inventory, self).action_confirm(cr, uid, ids, context)
        
        if context is None:
            context = {}

        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('stock.move')
        for inv in self.browse(cr, uid, ids, context=context):
            for line in inv.move_ids:
                location_id = line.product_id.product_tmpl_id.property_stock_inventory.id
                if line.location_id.id == location_id and line.prodlot_id:
                    move_ids = move_obj.search(cr, uid, [
                                                        ('prodlot_id', '=', line.prodlot_id.id),
                                                        ('state', '=', 'done'),
                                                        ('date', '<=', line.date),
                                                        ], order='date desc', limit=1)
                    if move_ids:
                        move_id = move_obj.browse(cr, uid , move_ids[0])
                        real_location_id = move_id.location_dest_id and move_id.location_dest_id.id
                        if real_location_id and real_location_id != location_id:
                            move_obj.write(cr, uid, line.id, {'location_id': real_location_id})
        return res

stock_inventory()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: