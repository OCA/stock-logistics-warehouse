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


class product_product(orm.Model):
    """Add the computation for the stock available to promise"""
    _inherit = 'product.product'

    def _product_available(self, cr, uid, ids, field_names=None, arg=False,
                           context=None):
        """Quantity available to promise based on components at hand."""
        # Compute the core quantities
        res = super(product_product, self)._product_available(
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

        # Compute the production capacity
        if any([f in field_names
                for f in ['potential_qty', 'immediately_usable_qty']]):
            # Compute the potential qty from BoMs with components available
            bom_obj = self.pool['mrp.bom']
            to_uom = 'uom' in context and self.pool['product.uom'].browse(
                cr, SUPERUSER_ID, context['uom'], context=context)

            for product in self.browse(cr, uid, ids, context=context):
                # _bom_find() returns a single BoM id.
                # We will not check any other BoM for this product
                bom_id = bom_obj._bom_find(cr, SUPERUSER_ID, product.id,
                                           product.uom_id.id)
                if bom_id:
                    min_qty = self._compute_potential_qty_from_bom(
                        cr, uid, bom_id, to_uom or product.uom_id,
                        context=context)

                    if 'potential_qty' in field_names:
                        res[product.id]['potential_qty'] += min_qty
                    if 'immediately_usable_qty' in field_names:
                        res[product.id]['immediately_usable_qty'] += min_qty

        return res

    def _compute_potential_qty_from_bom(self, cr, uid, bom_id, to_uom,
                                        context=None):
        """Compute the potential qty from BoMs with components available"""
        bom_obj = self.pool['mrp.bom']
        uom_obj = self.pool['product.uom']
        if context is None:
            context = {}
        if 'uom' in context:
            context_wo_uom = context.copy()
            del context_wo_uom['uom']
        else:
            context_wo_uom = context
        min_qty = False
        # Browse ignoring the UoM context to avoid cross-category conversions
        bom = bom_obj.browse(
            cr, uid, [bom_id], context=context_wo_uom)[0]

        # store id of final product uom

        for component in bom.bom_lines:
            # qty available in BOM line's UoM
            # XXX use context['uom'] instead?
            stock_component_qty = uom_obj._compute_qty_obj(
                cr, uid,
                component.product_id.uom_id,
                component.product_id.virtual_available,
                component.product_uom)
            # qty we can produce with this component, in the BoM's UoM
            bom_uom_qty = (stock_component_qty // component.product_qty
                           ) * bom.product_qty
            # Convert back to the reporting default UoM
            stock_product_uom_qty = uom_obj._compute_qty_obj(
                cr, uid, bom.product_uom, bom_uom_qty,
                to_uom)
            if min_qty is False:
                min_qty = stock_product_uom_qty
            elif stock_product_uom_qty < min_qty:
                min_qty = stock_product_uom_qty
        if min_qty < 0.0:
            min_qty = 0.0
        return min_qty

    _columns = {
        'potential_qty': fields.function(
            _product_available, method=True, multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Potential',
            help="Quantity of this Product that could be produced using "
                 "the materials already at hand, following a single level "
                 "of the Bills of Materials."),
    }
