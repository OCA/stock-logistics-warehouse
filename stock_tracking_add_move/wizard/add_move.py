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

class stock_packaging_move(osv.osv_memory):

    _name = "stock.packaging.move"
    
    _columns = {
        'reference': fields.char('Reference', size=128, required=True),
        'pack_id': fields.many2one('stock.tracking', 'Pack to move', required=True),
    }
    
    _defaults = {
        'pack_id': lambda s,cr,uid,c: c.get('active_id',False),
    }
    
    def add_move(self, cr, uid, ids, context=None):
        '''Init'''
        barcode_obj = self.pool.get('tr.barcode')
        tracking_obj = self.pool.get('stock.tracking')        
        if context == None:
            context = {}
             
        '''Get parent id'''
        parent_id = context.get('active_id',False)        
        for obj in self.browse(cr, uid, ids):
            ref = obj.reference
            barcode_ids = barcode_obj.search(cr, uid, [('code', '=', ref)], limit=1)
            if not barcode_ids:
                reference2 = ref
                while len(reference2.split('-')) > 1:
                    reference2 = reference2.replace('-','')
                barcode_ids = barcode_obj.search(cr, uid, [('code2', '=', reference2)], limit=1)
            ''' Call for the adding function '''
            tracking_obj.add_validation(cr, uid, [parent_id], barcode_ids, context=None) 
        return {'type': 'ir.actions.act_window_close'}
    
    def remove_move(self, cr, uid, ids, context=None):
        '''Init'''
        barcode_obj = self.pool.get('tr.barcode')
        tracking_obj = self.pool.get('stock.tracking')
        move_obj = self.pool.get('stock.move')
        to_validate_obj = self.pool.get('stock.scan.to.validate')              
        if context == None:
            context = {}
            
        '''Get parent id'''
        parent_id = context.get('active_id',False)        
        for obj in self.browse(cr, uid, ids):
            ref = obj.reference
            barcode_ids = barcode_obj.search(cr, uid, [('code', '=', ref)], limit=1)
            ''' Call for the removal function '''
            tracking_obj.remove_validation(cr, uid, [parent_id], barcode_ids, context=None) 
        return {'type': 'ir.actions.act_window_close'}    
       
stock_packaging_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: