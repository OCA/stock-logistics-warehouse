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

class stock_fill_inventory(osv.osv_memory):
    _inherit = "stock.fill.inventory"

    def _get_location(self, cr, uid, active_id, context={}):
        res = False
        if active_id:
            inv = self.pool.get('stock.inventory').browse(cr, uid, active_id)
            if inv.location_id:
                res = inv.location_id.id
        return res
        
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location', required=True),
    }

    _defaults = {
        'location_id': lambda s,cr,uid,c: s._get_location(cr, uid, c.get('active_id',False), c),
    }

stock_fill_inventory()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: