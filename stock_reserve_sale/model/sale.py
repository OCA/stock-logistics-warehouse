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
from openerp.tools.translate import _


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _stock_reservation(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for order_id in ids:
            result[order_id] = {'has_stock_reservation': False,
                                'is_stock_reservable': False}
        for sale in self.browse(cr, uid, ids, context=context):
            for line in sale.order_line:
                if line.reservation_ids:
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

    def action_button_confirm(self, cr, uid, ids, context=None):
        self.release_all_stock_reservation(cr, uid, ids, context=context)
        return super(sale_order, self).action_button_confirm(
            cr, uid, ids, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        self.release_all_stock_reservation(cr, uid, ids, context=context)
        return super(sale_order, self).action_cancel(
            cr, uid, ids, context=context)


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
            if not line.reservation_ids:
                result[line.id] = True
        return result

    _columns = {
        'reservation_ids': fields.one2many(
            'stock.reservation',
            'sale_line_id',
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
        default['reservation_ids'] = False
        return super(sale_order_line, self).copy_data(
            cr, uid, id, default=default, context=context)

    def release_stock_reservation(self, cr, uid, ids, context=None):
        lines = self.browse(cr, uid, ids, context=context)
        reserv_ids = [reserv.id for line in lines
                      for reserv in line.reservation_ids]
        reserv_obj = self.pool.get('stock.reservation')
        reserv_obj.release(cr, uid, reserv_ids, context=context)
        return True

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        result = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag, context=context)
        if not ids:  # warn only if we change an existing line
            return result
        assert len(ids) == 1, "Expected 1 ID, got %r" % ids
        line = self.browse(cr, uid, ids[0], context=context)
        if qty != line.product_uom_qty and line.reservation_ids:
            msg = _("As you changed the quantity of the line, "
                    "the quantity of the stock reservation will "
                    "be automatically adjusted to %.2f.") % qty
            msg += "\n\n"
            result.setdefault('warning', {})
            if result['warning'].get('message'):
                result['warning']['message'] += msg
            else:
                result['warning'] = {
                    'title': _('Configuration Error!'),
                    'message': msg,
                }
        return result

    def write(self, cr, uid, ids, vals, context=None):
        block_on_reserve = ('product_id',  'product_uom', 'product_uos',
                            'type')
        update_on_reserve = ('price_unit', 'product_uom_qty', 'product_uos_qty')
        keys = set(vals.keys())
        test_block = keys.intersection(block_on_reserve)
        test_update = keys.intersection(update_on_reserve)
        if test_block:
            for line in self.browse(cr, uid, ids, context=context):
                if not line.reservation_ids:
                    continue
                raise orm.except_orm(
                    _('Error'),
                    _('You cannot change the product or unit of measure '
                      'of lines with a stock reservation. '
                      'Release the reservation '
                      'before changing the product.'))
        res = super(sale_order_line, self).write(cr, uid, ids, vals, context=context)
        if test_update:
            for line in self.browse(cr, uid, ids, context=context):
                if not line.reservation_ids:
                    continue
                if len(line.reservation_ids) > 1:
                    raise orm.except_orm(
                        _('Error'),
                        _('Several stock reservations are linked with the '
                          'line. Impossible to adjust their quantity. '
                          'Please release the reservation '
                          'before changing the quantity.'))

                line.reservation_ids[0].write(
                    {'price_unit': line.price_unit,
                     'product_qty': line.product_uom_qty,
                     'product_uos_qty': line.product_uos_qty,
                     }
                )
        return res
