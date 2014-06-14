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

from openerp.osv import orm, fields
import decimal_precision as dp


class stock_valuation_history(orm.Model):
    """Record Products quantity & standard price for future reference.

    The unit price can be manually adjusted by users, and the total value is
    recomputed and cached.
    """
    _name = 'stock.valuation.history'
    _description = 'Stock inventory valuation'

    def _get_total_valuation(self, cr, uid, ids, fields, arg,
                             context=None):
        """Method for the function field 'total_valuation'"""
        valuations = self.browse(cr, uid, ids, context=context)
        return {v.id: v.standard_price * v.product_qty for v in valuations}

    _columns = {
        'name': fields.char(
            'Title', size=64, required=True, select=True,
            help="The title of the Stock Valuations. "
                 "Use the same title for all Stock Valuations "
                 "that form a logical set: for example if you "
                 "record the Valuation of all products after a "
                 "Physical Inventory, you should set the title "
                 "of all those Stock Valuations to the name of "
                 "the Physical Inventory."),
        'date': fields.datetime(
            'Date', readonly=True, required=True,
            help="The date on which this Stock Valuation was recorded."),
        'product_id': fields.many2one(
            'product.product', 'Product', ondelete='restrict', readonly=True),
        'category_id':  fields.related(
            'product_id', 'categ_id',
            relation='product.category', type='many2one', readonly=True,
            store=True, string='Product Category',
            help='This is the current Category of the Product.'),
        'label_ids':  fields.related(
            'product_id', 'label_ids', relation='product.label',
            type='many2many', readonly=True, string="Product Labels",
            help='These are the labels currently attached to this Product.'),
        'product_qty': fields.float(
            'Quantity',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            readonly=True,
            help="The Quantity of Product of this Stock Valuation."),
        'product_uom': fields.many2one(
            'product.uom', 'Unit of Measure', readonly=True,
            help="The Unit of Measure of this Stock Valuation."),
        # XXX avg is pretty lame since it's not weighted by quantity
        'standard_price': fields.float(
            'Valuation Price',
            digits_compute=dp.get_precision('Product Price'), required=True,
            group_operator='min',
            help="Unit Valuation Price of the Product at the date the "
                 "Stock Valuation was recorded. You can change this price "
                 "after it was recorded if you need to."),
        'total_valuation': fields.function(
            _get_total_valuation, method=True, type="float",
            string='Total Valuation',
            digits_compute=dp.get_precision('Account'),
            store={'stock.valuation.history': (
                lambda self, cr, uid, ids, context=None: ids,
                ['standard_price'], 10), },
            readonly=True),
    }

    _defaults = {
        'date': fields.date.context_today,
    }
