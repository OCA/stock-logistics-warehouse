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
import time

class stock_tracking(osv.osv):
    
    _inherit = 'stock.tracking'

    _columns = {
        'previous_id': fields.many2one('stock.tracking', 'Previous Pack', readonly=True),
        'modified': fields.boolean('Modified'),
    }
    
    _default = {
            'modified': False,
    }   
    '''Function for pack creation'''    
    def create_pack(self, cr, uid, ids, context=None):        
        '''Init'''
        if context == None:
            context = {}            
        '''Location determination'''
        stock_tracking_data = self.browse(cr, uid, ids[0])
        '''Pack Creation'''
        tracking_id = self.create(cr, uid, {'ul_id': stock_tracking_data.ul_id.id, 'location_id': stock_tracking_data.location_id.id})        
        '''Pack name is returned'''
        return tracking_id
    
    def reset_open(self, cr, uid, ids, context=None):
        res = super(stock_tracking, self).reset_open(cr, uid, ids, context)
        pack_ids = self.browse(cr, uid, ids, context)
        for pack in pack_ids:                        
            if pack.state == 'open':
                self.pool.get('stock.tracking.history').create(cr, uid, {
                                'type': 'reopen',
                                'previous_ref': pack.name,
                                'tracking_id': pack.id
                                }, context)
        return True

    def set_close(self, cr, uid, ids, context=None):
        
        barcode_obj = self.pool.get('tr.barcode')
        stock_move_obj = self.pool.get('stock.move')
        history_obj = self.pool.get('stock.tracking.history')
        res = super(stock_tracking, self).set_close(cr, uid, ids, context)
        if res:
            pack_ids = self.browse(cr, uid, ids, context)
            for pack in pack_ids:
                if pack.state == 'open':                
                    if self.pool.get('stock.tracking.history').search(cr,uid,[('type','=','reopen'),('tracking_id','=',pack.id)]) and pack.modified == True:           
                        new_pack_id = self.create_pack(cr, uid, ids, context)
                        new_pack_data = self.browse(cr, uid, new_pack_id, context)
                        '''loop on each move form the old pack to the new pack'''
                        for pack_move in pack.current_move_ids:
                            '''stock move creation'''
                            barcode_name = pack_move.prodlot_id.name
                            barcode_data = barcode_obj.search(cr, uid,[('code', '=', barcode_name)], limit=1)
                            move_id = stock_move_obj.create(cr, uid, {
                                                                      'name': pack_move.name,
                                                                      'state': pack_move.state,
                                                                      'product_id': pack_move.product_id.id,
                                                                      'product_uom': pack_move.product_uom.id,
                                                                      'prodlot_id': pack_move.prodlot_id.id,
                                                                      'location_id': pack.location_id.id,
                                                                      'location_dest_id': new_pack_data.location_id.id,
                                                                      'tracking_id': new_pack_data.id,
                                                                    })                            
                        '''end of loop''' 
                        if pack.child_ids:
                            for child_pack_data in pack.child_ids:
                                if child_pack_data.state == 'close':   
                                    self.write(cr, uid, child_pack_data.id, {'active': False})                                                          
                                    self.write(cr, uid, [new_child_pack_id], {'parent_id': new_pack_data.id,})
                                    history_obj.create(cr, uid, {'type': 'pack_in',
                                                                 'tracking_id': child_pack_data.id,
                                                                 'parent_id': new_pack_data.id,
                                                                })
                                    self.write(cr, uid, new_pack_data.id, {'location_id': child_pack_data.location_id and child_pack_data.location_id.id or False,})
                        
                        self.write(cr, uid, [pack.id], {'state': 'close',
                                                        'active': False,
                                                        'modified': False})
                        '''Call for a function who will display serial code list and product list in the pack layout'''                                                
                        self.get_products(cr, uid, [new_pack_data.id], context=None)
                        self.get_serials(cr, uid, [new_pack_data.id], context=None)
                        
                    self.write(cr, uid, [pack.id], {'state': 'close'})
        return res

stock_tracking()

class stock_tracking_history(osv.osv):
    
    _inherit = "stock.tracking.history"
    
    def _get_types(self, cr, uid, context={}):
        res = super(stock_tracking_history, self)._get_types(cr, uid, context)
        if not res:
            res = []
        res = res + [('reopen','Re Open')]
        return res
    
    _columns = {
        'type': fields.selection(_get_types, 'Type'),
        'previous_ref': fields.char('Previous reference', size=128),        
#        'previous_id': fields.many2one('stock.tracking', 'Previous pack'),
    }
    
stock_tracking_history()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
