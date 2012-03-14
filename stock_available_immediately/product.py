# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
#  Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
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


from osv import fields, osv
from tools.translate import _

class ProductImmediatelyUsable(osv.osv):
    """
    Inherit Product in order to add an "immediately usable quantity" stock field
    Immediately usable quantity is : real stock - outgoing qty
    """
    _inherit = 'product.product'
    
    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        # We need available and outgoing quantities to compute immediately usable quantity.
        # When immediately_usable_qty is displayed but not qty_available and outgoing_qty,
        # they are not computed in the super method so we cannot compute immediately_usable_qty.
        # To avoid this issue, we add the 2 fields in field_names to compute them.
        if 'immediately_usable_qty' in field_names:
            field_names.append('qty_available')
            field_names.append('outgoing_qty')
            
        res = super(ProductImmediatelyUsable, self)._product_available(cr, uid, ids, field_names, arg, context)
        
        if 'immediately_usable_qty' in field_names:        
            # for each product we compute the stock 
            for product_id, stock_qty in res.iteritems():
                res[product_id]['immediately_usable_qty'] = stock_qty['qty_available'] + stock_qty['outgoing_qty']
        
        return res
    
    _columns = {
        'qty_available': fields.function(_product_available, 
                                         method=True,
                                         type='float', 
                                         string='Real Stock', 
                                         multi='qty_available',
                                         help="Current quantities of products in selected locations or all internal if none have been selected."),
        'virtual_available': fields.function(_product_available, 
                                             method=True, 
                                             type='float', 
                                             string='Virtual Stock', 
                                             multi='qty_available',
                                             help="Futur stock for this product according to the selected location or all internal if none have been selected. Computed as: Real Stock - Outgoing + Incoming."),
        'incoming_qty': fields.function(_product_available, 
                                        method=True, 
                                        type='float', 
                                        string='Incoming', 
                                        multi='qty_available',
                                        help="Quantities of products that are planned to arrive in selected locations or all internal if none have been selected."),
        'outgoing_qty': fields.function(_product_available, 
                                        method=True, 
                                        type='float', 
                                        string='Outgoing', 
                                        multi='qty_available',
                                        help="Quantities of products that are planned to leave in selected locations or all internal if none have been selected."),    
        'immediately_usable_qty': fields.function(_product_available, 
                                                  method=True, 
                                                  type='float', 
                                                  string='Immediately Usable Stock', 
                                                  multi='qty_available',
                                                  help="Quantities of products really available for sale. Computed as: Real Stock - Outgoing."),
    }
    
    
ProductImmediatelyUsable()
