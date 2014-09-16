# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

import operator
from openerp.osv import orm, fields
from openerp.tools.translate import _


class StockLocation(orm.Model):
    _inherit = 'stock.location'

    def _product_value(self, cr, uid, ids, field_names, arg, context=None):
        _super = super(StockLocation, self)
        return _super._product_value(cr, uid, ids, field_names, arg,
                                     context=context)

    def _stock_search(self, cr, uid, obj, name, args, context=None):
        if not len(args):
            return []
        ops = {'<': operator.lt,
               '>': operator.gt,
               '=': operator.eq,
               '!=': operator.ne,
               '<=': operator.le,
               '>=': operator.ge,
               }
        location_ids = set()
        for field, symbol, value in args:
            if symbol not in ops:
                raise orm.except_orm(
                    _('Error'),
                    _('Operator %s not supported in '
                      'searches for Stock on Locations' % symbol))
            loc_ids = self.search(cr, uid, [], context=context)
            locations = self.read(cr, uid, loc_ids, [name],
                                  context=context)
            for location in locations:
                if ops[symbol](location[name], value):
                    location_ids.add(location['id'])
        return [('id', 'in', tuple(location_ids))]

    _columns = {
        'stock_real': fields.function(_product_value, type='float',
                                      fnct_search=_stock_search,
                                      string='Real Stock',
                                      multi="stock"),
        'stock_virtual': fields.function(_product_value, type='float',
                                         fnct_search=_stock_search,
                                         string='Virtual Stock',
                                         multi="stock"),
    }
