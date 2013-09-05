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


class stock_reservation(orm.Model):
    _inherit = 'stock.reservation'

    _columns = {
        'sale_line_id': fields.many2one(
            'sale.order.line',
            string='Sale Order Line',
            ondelete='cascade'),
        'sale_id': fields.related(
            'sale_line_id', 'order_id',
            type='many2one',
            relation='sale.order',
            string='Sale Order')
    }

    def release(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'sale_line_id': False}, context=context)
        return super(stock_reservation, self).release(
            cr, uid, ids, context=context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['sale_line_id'] = False
        return super(stock_reservation, self).copy_data(
            cr, uid, id, default=default, context=context)
