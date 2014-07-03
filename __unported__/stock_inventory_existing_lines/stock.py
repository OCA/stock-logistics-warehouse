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

class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    
    _columns = {
        'inventory_line_id2': fields.one2many('stock.inventory.line2', 'inventory_id', 'Inventories', states={'done': [('readonly', True)]}),
    }
    
    def action_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        '''  to perform the correct inventory corrections we need analyze stock location by
             location, never recursively, so we use a special context '''
        product_context = dict(context, compute_child=False)

        location_obj = self.pool.get('stock.location')
        line_obj = self.pool.get('stock.inventory.line')
        line2_obj = self.pool.get('stock.inventory.line2')
        for inv in self.browse(cr, uid, ids, context=context):
            move_ids = []
            for line in inv.inventory_line_id:    
#                ''' if the production lot is tracked but do not have a serial code then it is not taken into account '''    
#                if line.product_id.categ_id.tracked and not line.prod_lot_id:
#                    continue
                if not line.product_qty:
                    continue
                pid = line.product_id.id
                date = line.date or inv.date 
                product_context.update(uom=line.product_uom.id, date=date, to_date=date, prodlot_id=line.prod_lot_id.id)
                amount = location_obj._product_get(cr, uid, line.location_id.id, [pid], product_context)[pid]
                if not amount:
                    continue
                val_qty = min(line.product_qty,amount)
                if val_qty and val_qty > 0:
                    vals = line_obj.copy_data(cr, uid, line.id)
                    line2_obj.create(cr, uid, vals)
#                location_id = line.product_id.product_tmpl_id.property_stock_inventory.id
        res = super(stock_inventory, self).action_confirm(cr, uid, ids, context)
        return res

stock_inventory()

#class stock_move(osv.osv):
#    _inherit = "stock.move"
#    
#    _columns = {
#        'inventory_type': fields.selection([('in','In'),('out','Out')], 'Inventory type')
#    }
#stock_move()

class stock_inventory_line2(osv.osv):
    _name = "stock.inventory.line2"
    
    _columns = {
        'inventory_id': fields.many2one('stock.inventory', 'Inventory', ondelete='cascade', select=True),
        'location_id': fields.many2one('stock.location', 'Location', required=True),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
        'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
        'company_id': fields.related('inventory_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, select=True, readonly=True),
        'prod_lot_id': fields.many2one('stock.production.lot', 'Production Lot', domain="[('product_id','=',product_id)]"),
        'state': fields.related('inventory_id', 'state', type='char', string='State',readonly=True),
    }

stock_inventory_line2()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: