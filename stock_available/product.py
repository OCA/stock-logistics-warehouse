# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
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
import openerp.addons.decimal_precision as dp


# Expose the method as a function, like when the fields are defined,
# and use the pool to call the method from the other modules too.
def _product_available_fnct(self, cr, uid, ids, field_names=None, arg=False,
                            context=None):
    return self.pool['product.product']._product_available(
        cr, uid, ids, field_names=field_names, arg=arg, context=context)


class ProductProduct(orm.Model):
    """Add a field for the stock available to promise.

    Useful implementations need to be installed through the Settings menu or by
    installing one of the modules stock_available_*
    """
    _inherit = 'product.product'

    def __init__(self, pool, cr):
        """Use _product_available_fnct to compute all the quantities."""
        # Doing this lets us change the function and not redefine fields
        super(ProductProduct, self).__init__(pool, cr)
        for coldef in self._columns.values():
            if (isinstance(coldef, fields.function) and
                    coldef._multi == 'qty_available'):
                coldef._fnct = _product_available_fnct

    def _product_available(self, cr, uid, ids, field_names=None, arg=False,
                           context=None):
        """No-op implementation of the stock available to promise.

        Must be overridden by another module that actually implement
        computations.
        The sub-modules MUST call super()._product_available BEFORE their own
                computations
            AND call _update_virtual_available() AFTER their own computations
                with the context from the caller.

        Side-effect warning: By design, we want to change the behavior of the
            caller (make it aware that an extra field is being computed).
            For this, this method MAY change the list passed as the parameter
            `field_names`."""
        # If we didn't get a field_names list, there's nothing to do
        if field_names is None:
            return super(ProductProduct, self)._product_available(
                cr, uid, ids, field_names=field_names, arg=arg,
                context=context)

        if context is None:
            context = {}

        # Load virtual_available if it's not already asked for
        # We need it to compute immediately_usable_qty
        # We DO want to change the caller's list so we're NOT going to
        # work on a copy of field_names.
        if ('virtual_available' not in field_names and
                'immediately_usable_qty' in field_names):
            field_names.append('virtual_available')
        if context.get('virtual_is_immediately_usable', False):
            # _update_virtual_available will get/set these fields
            if 'virtual_available' not in field_names:
                field_names.append('virtual_available')
            if 'immediately_usable_qty' not in field_names:
                field_names.append('immediately_usable_qty')

        # Compute the core quantities
        res = super(ProductProduct, self)._product_available(
            cr, uid, ids, field_names=field_names, arg=arg, context=context)

        # By default, available to promise = forecasted quantity
        if ('immediately_usable_qty' in field_names):
            for stock_qty in res.itervalues():
                stock_qty['immediately_usable_qty'] = \
                    stock_qty['virtual_available']

        # _update_virtual_available would be useless here
        # It's up to the submodules to call it
        return res

    def _update_virtual_available(self, cr, uid, res, context=None):
        """Copy immediately_usable_qty to virtual_available if context asks

        @param context: If the key virtual_is_immediately_usable is True,
                        then the virtual stock is computed as the stock
                        available to promise. This lets existing code base
                        their computations on the new value with a minimum of
                        change (i.e.: warn salesmen when the stock available
                        for sale is insufficient to honor a quotation)"""
        if (context is None
                or not context.get('virtual_is_immediately_usable', False)):
            return res
        for stock_qty in res.itervalues():
            # _product_available makes sure both fields are loaded
            # We're changing the caller's state but it's not be a problem
            stock_qty['virtual_available'] = \
                stock_qty['immediately_usable_qty']
        return res

    _columns = {
        'immediately_usable_qty': fields.function(
            _product_available_fnct, multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Available to promise',
            help="Stock for this Product that can be safely proposed "
                 "for sale to Customers.\n"
                 "The definition of this value can be configured to suit "
                 "your needs"),
    }
