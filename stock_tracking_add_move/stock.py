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

class stock_tracking(osv.osv):
    
    _inherit = 'stock.tracking'

    _columns = {
        'parent_id': fields.many2one('stock.tracking', 'Parent', readonly=True),
        'child_ids': fields.one2many('stock.tracking', 'parent_id', 'Children', readonly=True),
        'to_add': fields.one2many('stock.scan.to.validate', 'tracking_id', 'To add', domain=[('type','=','in')]),
        'to_remove': fields.one2many('stock.scan.to.validate', 'tracking_id', 'To validate', domain=[('type','=','out')]),
    }
        
    def add_validation(self, cr, uid, ids, barcode_ids, context=None):
        
        barcode_obj = self.pool.get('tr.barcode')
        tracking_obj = self.pool.get('stock.tracking')
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        history_obj = self.pool.get('stock.tracking.history')
        validate_obj = self.pool.get('stock.scan.to.validate')
        
        if context == None:
            context = {}
        if barcode_ids:            
            for obj in self.browse(cr, uid, ids):
                barcode = barcode_obj.browse(cr, uid, barcode_ids[0])
                model = barcode.res_model
                res_id = barcode.res_id
                
                if model == 'stock.tracking':
                    '''Pack Case'''
                    pack = tracking_obj.browse(cr, uid, res_id)
                    ''' We can only add a closed pack '''
                    if pack.state == 'close':
                        tracking_obj.write(cr, uid, res_id, {'parent_id': obj.id,})
                        history_obj.create(cr, uid, {'type': 'pack_in',
                                                     'tracking_id': res_id,
                                                     'parent_id': obj.id,
                                                    })                        
                        tracking_obj.write(cr, uid, pack.id, {'location_id': obj.location_id and obj.location_id.id or False,})
                        tracking_obj.write(cr, uid, obj.id, {'modified': True})
                        for move_data in pack.move_ids:
                            if move_data.location_dest_id != tracking_obj.browse(cr, uid, obj.id).location_id:
                                new_move_id = move_obj.create(cr, uid, {'name': move_data.name,
                                                                        'state': 'draft',
                                                                        'product_id': move_data.product_id.id,
                                                                        'product_uom': move_data.product_uom.id,
                                                                        'prodlot_id': move_data.prodlot_id.id,
                                                                        'location_id': move_data.location_dest_id.id,
                                                                        'location_dest_id': obj.location_id.id,
                                                                        })
                elif model == 'stock.production.lot':
                    '''Production-lot Case'''
                    pack = tracking_obj.browse(cr, uid, obj.id)
                    move_ids = move_obj.search(cr, uid, [('state', '=', 'done'),
                                                         ('prodlot_id', '=', res_id),
                                                         ('date', '<=', pack.date)
#                                                         ('tracking_id', '=', False),
#                                                         ('location_dest_id', '=', pack.location_id and pack.location_id.id or False)
                                                         ], order='date desc', limit=1)
                    if move_ids:
                        move_data = move_obj.browse(cr, uid, move_ids[0])
                        if move_data.location_dest_id != pack.location_id:
                            new_move_id = move_obj.create(cr, uid, {'name': move_data.name,
                                                                    'state': 'draft',
                                                                    'product_id': move_data.product_id.id,
                                                                    'product_uom': move_data.product_uom.id,
                                                                    'prodlot_id': move_data.prodlot_id.id,
                                                                    'location_id': move_data.location_dest_id.id,
                                                                    'location_dest_id': obj.location_id.id,
                                                                    })
                            move_obj.write(cr, uid, new_move_id, {'tracking_id': obj.id})
                            tracking_obj.write(cr, uid, obj.id, {'modified': True}) 
                        else:    
                            move_obj.write(cr, uid, move_ids, {'tracking_id': obj.id})
                            tracking_obj.write(cr, uid, obj.id, {'modified': True})      
                        
                elif model == 'product.product':
                    '''Product Case'''                
                    pack = tracking_obj.browse(cr, uid, obj.id)  
                    product_data = product_obj.browse(cr, uid,res_id)                                 
                    move_id = move_obj.create(cr, uid, {
                                              'name': product_data.name,
                                              'product_id': product_data.id,
                                              'product_uom': product_data.uom_id.id,
                                              'location_id': pack.location_id.id,
                                              'location_dest_id': pack.location_id.id,
                                              'tracking_id': obj.id,
                                              'state': 'draft',
                                            })                        
                    tracking_obj.write(cr, uid, obj.id, {'modified': True})          
                        
            '''Call for a function who will display serial code list and product list in the pack layout'''                                                
            tracking_obj.get_products(cr, uid, ids, context=None)
            tracking_obj.get_serials(cr, uid, ids, context=None)   
        else:
            raise osv.except_osv(_('Warning!'),_('Barcode Not found!'))
        return {}
    
    def remove_validation(self, cr, uid, ids, barcode_ids, context=None):
        barcode_obj = self.pool.get('tr.barcode')
        tracking_obj = self.pool.get('stock.tracking')
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        history_obj = self.pool.get('stock.tracking.history')
        validate_obj = self.pool.get('stock.scan.to.validate')
        
        if context == None:
            context = {}
        if barcode_ids:
            for obj in self.browse(cr, uid, ids):
                barcode = barcode_obj.browse(cr, uid, barcode_ids[0])
                model = barcode.res_model
                res_id = barcode.res_id
                '''Pack Case'''
                if model == 'stock.tracking':
                    pack = tracking_obj.browse(cr, uid, res_id)
                    tracking_obj.write(cr, uid, res_id, {'parent_id': False})
                    tracking_obj.write(cr, uid, obj.id, {'modified': True})
                elif model == 'stock.production.lot':    
                    pack = tracking_obj.browse(cr, uid, obj.id)
                    move_ids = move_obj.search(cr, uid, [
                                     ('prodlot_id', '=', res_id),
                                     ], limit=1)
                    if move_ids:
                        move_obj.write(cr, uid, move_ids, {'tracking_id': False})
                        tracking_obj.write(cr, uid, obj.id, {'modified': True})        
                elif model == 'product.product':
                    pack = tracking_obj.browse(cr, uid, obj.id)  
                    product_data = product_obj.browse(cr, uid,res_id)
                    move_ids = move_obj.search(cr, uid, [
                                     ('product_id', '=', product_data.id),
                                     ], limit=1)     
                    if move_ids:
                        move_obj.write(cr, uid, move_ids, {'tracking_id': False})
                        tracking_obj.write(cr, uid, obj.id, {'modified': True})                           
                    
            '''Call for a function who will display serial code list and product list in the pack layout'''
            tracking_obj.get_serials(cr, uid, ids, context=None)
            tracking_obj.get_products(cr, uid, ids, context=None)            
        else:
            raise osv.except_osv(_('Warning!'),_('Barcode Not found!'))
        return {}     

stock_tracking()

class stock_scan_to_validate(osv.osv):
    
    _name = 'stock.scan.to.validate'
    _columns = {
        'tracking_id': fields.many2one('stock.tracking', 'Parent', readonly=True),
        'type': fields.selection([('in','To add'),('out','To remove')], 'Type', readonly=True),
        'barcode_id': fields.many2one('tr.barcode', 'Barcode', readonly=True),
    }
    
    _sql_constraints = [
        ('tracking_barcode_unique', 'unique (tracking_id,barcode_id)', 'This barcode is already in the list to add or to remove !')
    ]

stock_scan_to_validate()

class stock_tracking_history(osv.osv):
    
    _inherit = "stock.tracking.history"
    
    def _get_types(self, cr, uid, context={}):
        res = super(stock_tracking_history, self)._get_types(cr, uid, context)
        if not res:
            res = []
        res = res + [('pack_in','Add parent'),('pack_out','Unlink parent')]
        return res
    
    _columns = {
        'type': fields.selection(_get_types, 'Type'),
        'parent_id': fields.many2one('stock.tracking', 'Parent pack'),
    }
    
stock_tracking_history()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: