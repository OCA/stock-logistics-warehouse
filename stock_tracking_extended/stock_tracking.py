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

from datetime import datetime
from osv import fields, osv
from tools.translate import _
import netsvc

class one2many_special(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not values:
            values = {}
        res = {}
        location_ids = []
        for id in ids:
            res[id] = []
            location_id = obj.pool.get('stock.tracking').read(cr, user, id, ['location_id'])['location_id']
            if location_id and location_id[0] and location_id[0] not in location_ids:
                location_ids.append(location_id[0])
        ids2 = obj.pool.get(self._obj).search(cr, user, self._domain + [(self._fields_id, 'in', ids), ('location_dest_id', 'in', location_ids)], limit=self._limit)
        for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
            res[r[self._fields_id]].append( r['id'] )
        return res

class stock_tracking(osv.osv):
    
    _inherit = 'stock.tracking'
    
    def hierarchy_ids(self, tracking):
        result_list = [tracking]
        for child in tracking.child_ids:
            result_list.extend(self.hierarchy_ids(child))
        return result_list

    def _get_child_products(self, cr, uid, ids, field_name, arg, context=None):
        packs = self.browse(cr, uid, ids)
        res = {}
        for pack in packs:
            res[pack.id] = []
            childs = self.hierarchy_ids(pack)
            for child in childs:
                for prod in child.product_ids:
                    res[pack.id].append(prod.id)
        return res

    def _get_child_serials(self, cr, uid, ids, field_name, arg, context=None):
        packs = self.browse(cr, uid, ids)
        res = {}
        for pack in packs:
            res[pack.id] = []
            childs = self.hierarchy_ids(pack)
            for child in childs:
                for serial in child.serial_ids:
                    res[pack.id].append(serial.id)
        return res

    _columns = {
        'parent_id': fields.many2one('stock.tracking', 'Parent'),
        'child_ids': fields.one2many('stock.tracking', 'parent_id', 'Children', readonly=True),
        'ul_id': fields.many2one('product.ul', 'Logistic unit', readonly=True, states={'open':[('readonly',False)]}),
        'location_id': fields.many2one('stock.location', 'Location', required=True, readonly=True, states={'open':[('readonly',False)]}),
        'state': fields.selection([('open','Open'),('close','Close')], 'State', readonly=True),
        'product_ids': fields.one2many('product.stock.tracking', 'tracking_id', 'Products', readonly=True),
        'child_product_ids': fields.function(_get_child_products, method=True, type='one2many', obj='product.stock.tracking', string='Child Products'),
        'history_ids': fields.one2many('stock.tracking.history', 'tracking_id', 'History'),
        'current_move_ids': one2many_special('stock.move', 'tracking_id', 'Current moves', domain=[('pack_history_id', '=', False)], readonly=True),
        'name': fields.char('Pack Reference', size=64, required=True, readonly=True, states={'open':[('readonly',False)]}),
        'date': fields.datetime('Creation Date', required=True, readonly=True, states={'open':[('readonly',False)]}),
        'serial_ids': fields.one2many('serial.stock.tracking', 'tracking_id', 'Products', readonly=True),
        'child_serial_ids': fields.function(_get_child_serials, method=True, type='one2many', obj='serial.stock.tracking', string='Child Serials'),
    }
    
    def _check_parent_id(self, cr, uid, ids, context=None):
        lines = self.browse(cr, uid, ids, context=context)
        
        if lines[0].parent_id:
            if lines[0].ul_id.capacity_index > lines[0].parent_id.ul_id.capacity_index:
                return False
        return True
        
    _constraints = [(_check_parent_id, 'Bad parent type selection. Please try again.',['parent_id'] ),]
      
    _defaults = {
        'state': 'open',
    }
    
    def reset_open(self, cr, uid, ids, context=None):
        pack_ids = self.browse(cr, uid, ids, context)
        for pack in pack_ids:
            allowed = True
            if pack.parent_id:
                if pack.parent_id and pack.parent_id != 'open':
                    self.write(cr, uid, [pack.parent_id.id], {'state': 'open'})
#                    allowed = False
#                    raise osv.except_osv(_('Not allowed !'),_('You can\'t re-open this pack because the parent pack is close'))
            if allowed:
                for child in pack.child_ids:
                    if child.state == 'open':
                        allowed = False
                        raise osv.except_osv(_('Not allowed !'),_('You can\'t re-open this pack because there is at least one not closed child'))
                        break
            if allowed:
                self.write(cr, uid, [pack.id], {'state': 'open'})
        return True
    
    def set_close(self, cr, uid, ids, context=None):
        pack_ids = self.browse(cr, uid, ids, context)
        for pack in pack_ids:
            allowed = True
            for child in pack.child_ids:
                if child.state == 'open':
                    allowed = False
                    raise osv.except_osv(_('Not allowed !'),_('You can\'t close this pack because there is at least one not closed child'))
                    break
#            if allowed:
#                self.write(cr, uid, [pack.id], {'state': 'close'})
        return True
    
    def get_products(self, cr, uid, ids, context=None):
        pack_ids = self.browse(cr, uid, ids, context)
        stock_track = self.pool.get('product.stock.tracking')
        for pack in pack_ids:
            childs = self.hierarchy_ids(pack)
            for child in childs:
                product_ids = [x.id for x in child.product_ids]
                stock_track.unlink(cr, uid, product_ids)
                product_list = {}
                for x in child.current_move_ids:
                    if x.location_dest_id.id == child.location_id.id:
                        if x.product_id.id not in product_list.keys():
                            product_list.update({x.product_id.id:x.product_qty})
                        else:
                            product_list[x.product_id.id] += x.product_qty
                for product in product_list.keys():
                    stock_track.create(cr, uid, {'product_id': product, 'quantity': product_list[product], 'tracking_id': child.id})
        return True
    
    def get_serials(self, cr, uid, ids, context=None):
        pack_ids = self.browse(cr, uid, ids, context)
        serial_track = self.pool.get('serial.stock.tracking')
        serial_obj = self.pool.get('stock.production.lot')
        for pack in pack_ids:
            childs = self.hierarchy_ids(pack)
            for child in childs:
                serial_ids = [x.id for x in child.serial_ids]
                serial_track.unlink(cr, uid, serial_ids)
                serial_list = {}
                for x in child.current_move_ids:
                    if x.location_dest_id.id == child.location_id.id:
                        if x.prodlot_id.id not in serial_list.keys():
                            serial_list.update({x.prodlot_id.id:x.product_qty})
                        else:
                            serial_list[x.prodlot_id.id] += x.product_qty
                for serial in serial_list.keys():
                    if serial:
                        serial_track.create(cr, uid, {'serial_id': serial, 'quantity': serial_list[serial], 'tracking_id': child.id})
                        serial_obj.write(cr, uid, [serial], {'tracking_id': child.id})
        return True

stock_tracking()

class product_ul(osv.osv):
    _inherit = "product.ul" 
    _description = "Shipping Unit"
    _columns = {
         'capacity_index': fields.integer('Capacity index'),
    }
    _order = 'capacity_index'
product_ul()

class product_stock_tracking(osv.osv):
    
    _name = 'product.stock.tracking'

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'quantity': fields.float('Quantity'),
        'tracking_id': fields.many2one('stock.tracking', 'Tracking'),
#        'tracking_history_id': fields.many2one('stock.tracking.history', 'Tracking History'),
    }
    
product_stock_tracking()

class serial_stock_tracking(osv.osv):
    
    _name = 'serial.stock.tracking'
    
    _order = 'tracking_id,serial_id'

    _columns = {
        'serial_id': fields.many2one('stock.production.lot', 'Serial'),
        'product_id': fields.related('serial_id', 'product_id', type='many2one', relation='product.product', string='Product'),
        'quantity': fields.float('Quantity'),
        'tracking_id': fields.many2one('stock.tracking', 'Tracking'),
#        'tracking_history_id': fields.many2one('stock.tracking.history', 'Tracking History'),
    }
    
serial_stock_tracking()

class stock_tracking_history(osv.osv):

    _name = "stock.tracking.history"
    
    def _get_types(self, cr, uid, context={}):
#        res = [('pack_in','Add parent'),('pack_out','Unlink parent'),('move','Move')]
        res = []
        return res
    
#    def hierarchy_ids(self, tracking):
#        result_list = [tracking]
#        for child in tracking.child_ids:
#            result_list.extend(self.hierarchy_ids(child))
#        return result_list
#    
#    def _get_child_products(self, cr, uid, ids, field_name, arg, context=None):
#        packs = self.browse(cr, uid, ids)
#        res = {}
#        for pack in packs:
#            res[pack.id] = []
#            childs = self.hierarchy_ids(pack)
#            for child in childs:
#                for prod in child.product_ids:
#                    res[pack.id].append(prod.id)
#        return res
    
    _columns = {
        'tracking_id': fields.many2one('stock.tracking', 'Pack', required=True),
        'type': fields.selection(_get_types, 'Type'),
#        'product_ids': fields.one2many('product.stock.tracking', 'tracking_history_id', 'Products'),
#        'child_product_ids': fields.function(_get_child_products, method=True, type='one2many', obj='product.stock.tracking', string='Child Products'),
#        'parent_hist_id': fields.many2one('stock.tracking.history', 'Parent history pack'),
#        'child_ids': fields.one2many('stock.tracking.history', 'parent_hist_id', 'Child history pack'),
    }
    
    _rec_name = "tracking_id"
    
stock_tracking_history()

'''Add a field in order to store the current pack in a production lot'''
class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'    
    _columns = {
        'tracking_id': fields.many2one('stock.tracking', 'pack'),
    }
    
stock_production_lot()

class product_category(osv.osv):   
    _inherit = 'product.category'    
    _columns = {
        'tracked': fields.boolean('Need a serial code ?'),
    }    
product_category()

class stock_inventory(osv.osv):
    _inherit = 'stock.inventory'    
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'stock.inventory') or '/'
    }
stock_inventory()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
         'move_ori_id': fields.many2one('stock.move', 'Origin Move', select=True),       
#        'cancel_cascade': fields.boolean('Cancel Cascade', help='If checked, when this move is cancelled, cancel the linked move too')
    }
    
    def write(self, cr, uid, ids, vals, context=None):  
        result = super(stock_move,self).write(cr, uid, ids, vals, context)
        if not isinstance(ids, list):
            ids = [ids]
        for id in ids:
            state = self.browse(cr, uid, id, context).state
            move_ori_id = self.browse(cr, uid, id, context).move_ori_id
            if state == 'done' and move_ori_id:
                self.write(cr, uid, [move_ori_id], {'state':'done'}, context)                 
        return result
    
    def create(self, cr, uid, vals, context=None):     
        production_lot_obj = self.pool.get('stock.production.lot')        
        stock_tracking_obj = self.pool.get('stock.tracking')
        if vals.get('prodlot_id',False):
            production_lot_data = production_lot_obj.browse(cr, uid, vals['prodlot_id'])
            last_production_lot_move_id = self.search(cr, uid, [('prodlot_id', '=', production_lot_data.id)], limit=1, order='date')
            if last_production_lot_move_id:
                last_production_lot_move = self.browse(cr,uid,last_production_lot_move_id[0])
                if last_production_lot_move.tracking_id:
                    ids = [last_production_lot_move.tracking_id.id]
                    stock_tracking_obj.reset_open(cr, uid, ids, context=None)
        
        return super(stock_move,self).create(cr, uid, vals, context)
    
stock_move()

class split_in_production_lot(osv.osv_memory):
    _inherit = "stock.move.split"
    _columns = {
        'use_exist' : fields.boolean('Existing Lots', invisible=True),
     }
    _defaults = {
        'use_exist': lambda *a: True,
    }
    def default_get(self, cr, uid, fields, context=None):        
        res = super(split_in_production_lot, self).default_get(cr, uid, fields, context)
        res.update({'use_exist': True})
        return res
    
split_in_production_lot()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
