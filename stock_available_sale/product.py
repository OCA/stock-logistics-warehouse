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

from openerp import SUPERUSER_ID
from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp

# Function which uses the pool to call the method from the other modules too.
from openerp.addons.stock_available import _product_available_fnct


class ProductProduct(orm.Model):
    """Add the computation for the stock available to promise"""
    _inherit = 'product.product'

    def _product_available(self, cr, uid, ids, field_names=None, arg=False,
                           context=None):
        """Compute the quantities in Quotations."""
        # Compute the core quantities
        res = super(ProductProduct, self)._product_available(
            cr, uid, ids, field_names=field_names, arg=arg, context=context)
        # If we didn't get a field_names list, there's nothing to do
        if field_names is None:
            return res

        if context is None:
            context = {}
        # Prepare an alternative context without 'uom', to avoid cross-category
        # conversions when reading the available stock of components
        if 'uom' in context:
            context_wo_uom = context.copy()
            del context_wo_uom['uom']
        else:
            context_wo_uom = context
        # Compute the quantities quoted/available to promise
        if any([f in field_names
                for f in ['quoted_qty', 'immediately_usable_qty']]):
            date_str, date_args = self._get_dates(cr, uid, ids,
                                                  context=context)

            # Limit the search to some shops according to the context
            shop_str, shop_args = self._get_shops(cr, uid, ids,
                                                  context=context)

            # Query the total by Product and UoM
            cr.execute(
                """
                SELECT sum(product_uom_qty), product_id, product_uom
                FROM sale_order_line
                INNER JOIN sale_order
                     ON (sale_order_line.order_id = sale_order.id)
                WHERE product_id in %s
                      AND sale_order_line.state = 'draft' """
                + date_str + shop_str +
                "GROUP BY sale_order_line.product_id, product_uom",
                (tuple(ids),) + date_args + shop_args)
            results = cr.fetchall()

            # Get the UoM resources we'll need for conversion
            # UoMs from the products
            uoms_o = {}
            product2uom = {}
            for product in self.browse(cr, uid, ids, context=context):
                product2uom[product.id] = product.uom_id
                uoms_o[product.uom_id.id] = product.uom_id
            # UoM from the results and the context
            uom_obj = self.pool['product.uom']
            uoms = map(lambda stock_product_uom_qty: stock_product_uom_qty[2],
                       results)
            if context.get('uom', False):
                uoms.append(context['uom'])
            uoms = filter(lambda stock_product_uom_qty:
                          stock_product_uom_qty not in uoms_o.keys(), uoms)
            if uoms:
                uoms = uom_obj.browse(cr, SUPERUSER_ID, list(set(uoms)),
                                      context=context)
            for o in uoms:
                uoms_o[o.id] = o

            # Compute the quoted quantity
            for (amount, prod_id, prod_uom) in results:
                # Convert the amount to the product's UoM without rounding
                amount = amount / uoms_o[prod_uom].factor
                if 'quoted_qty' in field_names:
                    res[prod_id]['quoted_qty'] -= amount
                if 'immediately_usable_qty' in field_names:
                    res[prod_id]['immediately_usable_qty'] -= amount

            # Round and optionally convert the results to the requested UoM
            for prod_id, stock_qty in res.iteritems():
                if context.get('uom', False):
                    # Convert to the requested UoM
                    res_uom = uoms_o[context['uom']]
                else:
                    # The conversion is unneeded but we do need the rounding
                    res_uom = product2uom[prod_id]
                if 'quoted_qty' in field_names:
                    stock_qty['quoted_qty'] = uom_obj._compute_qty_obj(
                        cr, SUPERUSER_ID, product2uom[prod_id],
                        stock_qty['quoted_qty'],
                        res_uom)
                if 'immediately_usable_qty' in field_names:
                    stock_qty['immediately_usable_qty'] = \
                        uom_obj._compute_qty_obj(
                            cr, SUPERUSER_ID, product2uom[prod_id],
                            stock_qty['immediately_usable_qty'],
                            res_uom)
        return res

    def _get_shops(self, cr, uid, ids, context=None):
        """Find the shops matching the current context

        See the helptext for the field quoted_qty for details"""
        shop_ids = []
        # Account for one or several locations in the context
        # Take any shop using any warehouse that has these locations as stock
        # location
        if context.get('location', False):
            # Either a single or multiple locations can be in the context
            if isinstance(context['location'], (int, long)):
                location_ids = [context['location']]
            else:
                location_ids = context['location']
            # Add the children locations
            if context.get('compute_child', True):
                child_location_ids = self.pool['stock.location'].search(
                    cr, SUPERUSER_ID,
                    [('location_id', 'child_of', location_ids)])
                location_ids = child_location_ids or location_ids
            # Get the corresponding Shops
            cr.execute(
                """
                SELECT id FROM sale_shop
                WHERE warehouse_id IN (
                    SELECT id
                    FROM stock_warehouse
                    WHERE lot_stock_id IN %s)""",
                (tuple(location_ids),))
            res_location = cr.fetchone()
            if res_location:
                shop_ids.append(res_location)

        # Account for a warehouse in the context
        # Take any draft order in any shop using this warehouse
        if context.get('warehouse', False):
            cr.execute("SELECT id "
                       "FROM sale_shop "
                       "WHERE warehouse_id = %s",
                       (int(context['warehouse']),))
            res_wh = cr.fetchone()
            if res_wh:
                shop_ids.append(res_wh)

        # If we are in a single Shop context, only count the quotations from
        # this shop
        if context.get('shop', False):
            shop_ids.append(context['shop'])
        # Build the SQL to restrict to the selected shops
        shop_str = ''
        if shop_ids:
            shop_str = 'AND sale_order.shop_id IN %s'

        if shop_ids:
            shop_ids = (tuple(shop_ids),)
        else:
            shop_ids = ()
        return shop_str, shop_ids

    def _get_dates(self, cr, uid, ids, context=None):
        """Build SQL criteria to match the context's from/to dates"""
        # If we are in a context with dates, only consider the quotations to be
        # delivered at these dates.
        # If no delivery date was entered, use the order date instead
        if not context:
            return '', ()

        from_date = context.get('from_date', False)
        to_date = context.get('to_date', False)
        date_str = ''
        date_args = []
        if from_date:
            date_str = """AND COALESCE(
                              sale_order.requested_date,
                              sale_order.date_order) >= %s """
            date_args.append(from_date)
        if to_date:
            date_str += """AND COALESCE(
                               sale_order.requested_date,
                               sale_order.date_order) <= %s """
            date_args.append(to_date)

        if date_args:
            date_args = (tuple(date_args),)
        else:
            date_args = ()
        return date_str, date_args

    _columns = {
        'quoted_qty': fields.function(
            _product_available_fnct, method=True, multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quoted',
            help="Total quantity of this Product that have been included in "
                 "Quotations (Draft Sale Orders).\n"
                 "In a context with a single Shop, this includes the "
                 "Quotation processed at this Shop.\n"
                 "In a context with a single Warehouse, this includes "
                 "Quotation processed in any Shop using this Warehouse.\n"
                 "In a context with a single Stock Location, this includes "
                 "Quotation processed at any shop using any Warehouse using "
                 "this Location, or any of its children, as it's Stock "
                 "Location.\n"
                 "Otherwise, this includes every Quotation."),
    }
