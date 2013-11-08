# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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
##############################################################################

from openerp.osv import orm, fields


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_move(self, cr, uid, order, line, picking_id,
                                 date_planned, context=None):
        values = super(sale_order, self)._prepare_order_line_move(
            cr, uid, order, line, picking_id, date_planned, context=context)
        if line.location_id:
            values['location_id'] = line.location_id.id
        return values

    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id, date_planned,
                                        context=None):
        values = super(sale_order, self)._prepare_order_line_procurement(
            cr, uid, order, line, move_id, date_planned, context=context)
        if line.location_id:
            values['location_id'] = line.location_id.id
        return values


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'location_id': fields.many2one(
            'stock.location',
            'Source Location',
            help="If a source location is selected, "
                 "it will be used as source of the stock moves. "),
    }
