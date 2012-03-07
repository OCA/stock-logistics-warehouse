# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp

class product_product(osv.osv):
    
    _inherit = "product.product"

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context={}):
        if not field_names:
            field_names = []
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
        for f in field_names:
            c = context.copy()
            if f == 'qty_available':
                c.update({ 'states':('done',), 'what':('in', 'out') })
            if f == 'virtual_available':
                c.update({ 'states':('confirmed','waiting','assigned','on_hold','on_hold_billing','on_hold_paym','done'), 'what':('in', 'out') })
            if f == 'incoming_qty':
                c.update({ 'states':('confirmed','waiting','assigned','on_hold','on_hold_billing','on_hold_paym'), 'what':('in',) })
            if f == 'outgoing_qty':
                c.update({ 'states':('confirmed','waiting','assigned','on_hold','on_hold_billing','on_hold_paym'), 'what':('out',) })
            stock = self.get_product_available(cr,uid,ids,context=c)
            for id in ids:
                res[id][f] = stock.get(id, 0.0)
        return res

    _columns = {
        'qty_available': fields.function(_product_available, method=True, type='float', string='Real Stock', help="Current quantities of products in selected locations or all internal if none have been selected.", multi='qty_available', digits_compute=dp.get_precision('Product UoM')),
        'virtual_available': fields.function(_product_available, method=True, type='float', string='Virtual Stock', help="Future stock for this product according to the selected location or all internal if none have been selected. Computed as: Real Stock - Outgoing + Incoming.", multi='qty_available', digits_compute=dp.get_precision('Product UoM')),
        'incoming_qty': fields.function(_product_available, method=True, type='float', string='Incoming', help="Quantities of products that are planned to arrive in selected locations or all internal if none have been selected.", multi='qty_available', digits_compute=dp.get_precision('Product UoM')),
        'outgoing_qty': fields.function(_product_available, method=True, type='float', string='Outgoing', help="Quantities of products that are planned to leave in selected locations or all internal if none have been selected.", multi='qty_available', digits_compute=dp.get_precision('Product UoM')),
    }
    
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
