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

from openerp.osv import orm


class product_immediately_usable(orm.Model):
    """Subtract incoming qty from immediately_usable_qty

    We don't need to override the function fields, the module stock_available
    takes care of it for us."""
    _inherit = 'product.product'

    def _product_available(self, cr, uid, ids, field_names=None,
                           arg=False, context=None):
        """Ignore the incoming goods in the quantity available to promise

        Side-effect warning: By design, we want to change the behavior of the
            caller (make it aware that an extra field is being computed).
            For this, this method MAY change the list passed as the parameter
            `field_names`."""
        # If we didn't get a field_names list, there's nothing to do
        if field_names is None or 'immediately_usable_qty' not in field_names:
            return super(product_immediately_usable, self)._product_available(
                cr, uid, ids, field_names=field_names, arg=arg,
                context=context)

        # We need available and incoming quantities to compute
        # immediately usable quantity.
        # We DO want to change the caller's list so we're NOT going to
        # work on a copy of field_names.
        field_names.append('qty_available')
        field_names.append('incoming_qty')

        res = super(product_immediately_usable, self)._product_available(
            cr, uid, ids, field_names=field_names, arg=arg, context=context)

        for stock_qty in res.itervalues():
            stock_qty['immediately_usable_qty'] -= \
                stock_qty['incoming_qty']

        return res
