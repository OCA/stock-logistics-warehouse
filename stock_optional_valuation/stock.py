# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _

class stock_location(orm.Model):
    _inherit = "stock.location"
    
    _columns = {
        'consider_internal': fields.boolean('Consider internal', help="Consider as internal location for inventory valuation: stock moves from internal to internal will not generate accounting entries"),
        }

class stock_move(orm.Model):
    _inherit = "stock.move"
    
    def _create_product_valuation_moves(self, cr, uid, move, context=None):
        if (move.location_id.company_id and move.location_dest_id.company_id
            and move.location_id.company_id != move.location_dest_id.company_id):
            return super(stock_move,self)._create_product_valuation_moves(
                cr, uid, move, context=context)
        if (move.location_id.usage == 'internal' or
            move.location_id.consider_internal) and (
            move.location_dest_id.usage == 'internal' or
            move.location_dest_id.consider_internal):
            return
        return super(stock_move,self)._create_product_valuation_moves(
            cr, uid, move, context=context)
