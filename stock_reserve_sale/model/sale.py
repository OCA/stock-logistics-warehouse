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

    def _stock_reservation(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for order_id in ids:
            result[order_id] = {'has_stock_reservation': False,
                                'is_stock_reservable': False}
        for sale in self.browse(cr, uid, ids, context=context):
            for line in sale.order_line:
                if line.reservation_id:
                    result[sale.id]['has_stock_reservation'] = True
                if line.is_stock_reservable:
                    result[sale.id]['is_stock_reservable'] = True
            if sale.state not in ('draft', 'sent'):
                result[sale.id]['is_stock_reservable'] = False
        return result

    _columns = {
        'has_stock_reservation': fields.function(
            _stock_reservation,
            type='boolean',
            readonly=True,
            multi='stock_reservation',
            string='Has Stock Reservations'),
        'is_stock_reservable': fields.function(
            _stock_reservation,
            type='boolean',
            readonly=True,
            multi='stock_reservation',
            string='Can Have Stock Reservations'),
    }

    def release_all_stock_reservation(self, cr, uid, ids, context=None):
        sales = self.browse(cr, uid, ids, context=context)
        line_ids = [line.id for sale in sales for line in sale.order_line]
        line_obj = self.pool.get('sale.order.line')
        line_obj.release_stock_reservation(cr, uid, line_ids, context=context)
        return True


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    def _is_stock_reservable(self, cr, uid, ids, fields, args, context=None):
        result = {}.fromkeys(ids, False)
        for line in self.browse(cr, uid, ids, context=context):
            if line.state != 'draft':
                continue
            if line.type == 'make_to_order':
                continue
            if (not line.product_id or line.product_id.type == 'service'):
                continue
            if not line.reservation_id:
                result[line.id] = True
        return result

    _columns = {
        'reservation_id': fields.many2one(
            'stock.reservation',
            string='Stock Reservation'),
        'is_stock_reservable': fields.function(
            _is_stock_reservable,
            type='boolean',
            readonly=True,
            string='Can be reserved'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['reservation_id'] = False
        return super(sale_order_line, self).copy_data(
            cr, uid, id, default=default, context=context)

    def release_stock_reservation(self, cr, uid, ids, context=None):
        lines = self.browse(cr, uid, ids, context=context)
        reserv_ids = [line.reservation_id.id for line in lines
                      if line.reservation_id]
        reserv_obj = self.pool.get('stock.reservation')
        reserv_obj.release(cr, uid, reserv_ids, context=context)
        self.write(cr, uid, ids, {'reservation_id': False}, context=context)
        return True

    def update_stock_reservation(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if not line.reservation_id:
                continue
            line.reservation_id.write({'product_qty': line.product_uom_qty,
                                       'product_uom': line.product_uom.id})
        return True
