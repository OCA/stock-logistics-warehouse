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
            if (isinstance(coldef, fields.function)
                    and coldef._multi == 'qty_available'):
                coldef._fnct = _product_available_fnct

    def _product_available(self, cr, uid, ids, field_names=None, arg=False,
                           context=None):
        """No-op implementation of the stock available to promise.

        Must be overridden by another module that actually implement
        computations.
        The sub-modules MUST call super()._product_available BEFORE their own
                computations

        Side-effect warning: This method may change the list passed as the
            field_names parameter, which will then alter the caller's state."""
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
        if ('virtual_available' not in field_names
                and 'immediately_usable_qty' in field_names):
            field_names.append('virtual_available')

        # Compute the core quantities
        res = super(ProductProduct, self)._product_available(
            cr, uid, ids, field_names=field_names, arg=arg, context=context)

        # By default, available to promise = forecasted quantity
        if ('immediately_usable_qty' in field_names):
            for stock_qty in res.itervalues():
                stock_qty['immediately_usable_qty'] = \
                    stock_qty['virtual_available']

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
