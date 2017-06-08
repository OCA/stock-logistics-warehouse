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

import time

from openerp.osv import orm
from openerp.tools.translate import _
from openerp import tools


class ProductProduct(orm.Model):
    """Add methods to record the valuation"""
    _inherit = 'product.product'

    def create_valuation(self, cr, uid, ids, context=None):
        """Record the valuation of the products

        @param ids: list of product IDs
        @param context: 'product_uom': UoM conversion will be attempted.
                        'date': the quantity will be queried at that date-time
                                and the valuation will be recorded at that
                                date-time.
                                WARNING! the price CANNOT be queried at that
                                date, so it may be inconsistent.
                        'name': all created records will have that name instead
                                of the name of the product
                        Other keys may be added to tweak the way quantities are
                        queried (shop, warehouse...)
        @return IDs of the created valuation records"""
        if context is None:
            context = {}

        # Remove duplicates
        ids = list(set(ids))

        valuation_ids = []
        val_obj = self.pool['stock.valuation.history']
        # Default name
        name = context.get(
            "name", _("Valuation as of %s") % time.strftime(
                tools.DEFAULT_SERVER_DATE_FORMAT))

        for product in self.browse(cr, uid, ids, context=context):
            default = {
                'product_id': product.id,
                'name': name,
                'standard_price': product.standard_price,
                'product_uom': context.get("uom", product.uom_id.id),
                'product_qty': product.qty_available,
            }
            if 'date' in context:
                default['date'] = context['date']
            valuation_ids.append(val_obj.create(
                cr, uid, default, context=context))
        return valuation_ids

    def search_create_valuation(self, cr, uid, args, context=None):
        """Search for products and record the valuation of the products

        @param values: values values of the valuation records
        @return IDs of the created valuation records"""
        return self.create_valuation(
            cr, uid, self.search(cr, uid, args, context=context),
            context=context)
