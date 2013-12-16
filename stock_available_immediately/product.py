# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2010-2012 Camptocamp SA
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
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

from openerp.addons import decimal_precision as dp

from openerp.osv import orm, fields


class product_immediately_usable(orm.Model):
    """
    Inherit Product in order to add an "immediately usable quantity"
    stock field
    Immediately usable quantity is : real stock - outgoing qty
    """
    _inherit = 'product.product'

    def _product_available(self, cr, uid, ids, field_names=None,
                           arg=False, context=None):
        """
        Get super() _product_available and compute immediately_usable_qty
        """
        # We need available and outgoing quantities to compute
        # immediately usable quantity.
        # When immediately_usable_qty is displayed but
        # not qty_available and outgoing_qty,
        # they are not computed in the super method so we cannot
        # compute immediately_usable_qty.
        # To avoid this issue, we add the 2 fields in
        # field_names to compute them.
        if 'immediately_usable_qty' in field_names:
            field_names.append('qty_available')
            field_names.append('outgoing_qty')

        res = super(product_immediately_usable, self)._product_available(
            cr, uid, ids, field_names, arg, context)

        if 'immediately_usable_qty' in field_names:
            for product_id, stock_qty in res.iteritems():
                res[product_id]['immediately_usable_qty'] = \
                    stock_qty['qty_available'] + stock_qty['outgoing_qty']

        return res

    _columns = {
        'qty_available': fields.function(
            _product_available,
            multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product UoM'),
            string='Quantity On Hand',
            help="Current quantity of products.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, "
                 "or any "
                 "of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "typed as 'internal'."),
        'virtual_available': fields.function(
            _product_available,
            multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product UoM'),
            string='Quantity Available',
            help="Forecast quantity (computed as Quantity On Hand "
                 "- Outgoing + Incoming)\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, "
                 "or any "
                 "of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "typed as 'internal'."),
        'incoming_qty': fields.function(
            _product_available,
            multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product UoM'),
            string='Incoming',
            help="Quantity of products that are planned to arrive.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods arriving to this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods arriving to the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "arriving to the Stock Location of the Warehouse of this "
                 "Shop, or any of its children.\n"
                 "Otherwise, this includes goods arriving to any Stock "
                 "Location typed as 'internal'."),
        'outgoing_qty': fields.function(
            _product_available,
            multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product UoM'),
            string='Outgoing',
            help="Quantity of products that are planned to leave.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods leaving from this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods leaving from the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "leaving from the Stock Location of the Warehouse of this "
                 "Shop, or any of its children.\n"
                 "Otherwise, this includes goods leaving from any Stock "
                 "Location typed as 'internal'."),
        'immediately_usable_qty': fields.function(
            _product_available,
            digits_compute=dp.get_precision('Product UoM'),
            type='float',
            string='Immediately Usable',
            multi='qty_available',
            help="Quantity of products really available for sale." \
                 "Computed as: Quantity On Hand - Outgoing."),
    }
