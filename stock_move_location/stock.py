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

#class stock_fill_inventory(osv.osv_memory):
#    _inherit = "stock.fill.inventory"
#    def fill_inventory(self, cr, uid, ids, context=None):
#        res = super(stock_fill_inventory, self).fill_inventory(cr, uid, ids, context=context)
#        stock_inventory_obj = self.pool.get('stock.inventory')
#        fill_inventory = self.browse(cr, uid, ids[0], context=context)
#        if stock_inventory_obj.browse(cr, uid, context.get('active_id', False), context).location_id:
#            stock_inventory_obj.write(cr, uid, context.get('active_id', False), {'location_id': fill_inventory.location_id.id})
#        return res
#stock_fill_inventory()

class stock_inventory(osv.osv):
    _inherit = "stock.inventory"

    _columns = {
        'type': fields.selection([('normal', 'Inventory'),('move', 'Location Move')], 'Type'),
        'location_id': fields.many2one('stock.location', 'Location'),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location'),
        'comments':fields.text('Comments'),
    }

    def get_sequence(self, cr , uid, context):
        if context.get('type', False) == 'move':
            return self.pool.get('ir.sequence').get(cr, uid, 'stock.inventory.move') or '/'
        else:
            return self.pool.get('ir.sequence').get(cr, uid, 'stock.inventory') or '/'

    _defaults = {
        'type': lambda *a: 'normal',
        'name': lambda x, y, z, c: x.get_sequence(y,z,c),
    }

    def move_stock(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        product_context = dict(context, compute_child=False)

        location_obj = self.pool.get('stock.location')
        for inv in self.browse(cr, uid, ids, context=context):
            if not inv.location_dest_id:
                raise osv.except_osv(_('Error !'), _('Please inform the destination of your move'))
            move_ids = []
            for line in inv.inventory_line_id:
                location_id = inv.location_dest_id.id
                date = line.date or inv.date
                value = {
                    'name': 'MOVE:' + str(line.inventory_id.id) + ':' + line.inventory_id.name,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'prodlot_id': line.prod_lot_id.id,
                    'date': date,
                    'product_qty': line.product_qty,
                    'location_id': line.location_id.id,
                    'location_dest_id': location_id,
                    'note': line.note or inv.comments or False,
                }
                move_ids.append(self._inventory_line_hook(cr, uid, line, value))
            message = _('Move') + " '" + inv.name + "' "+ _("is done.")
            self.log(cr, uid, inv.id, message)
            self.write(cr, uid, [inv.id], {'state': 'confirm', 'move_ids': [(6, 0, move_ids)]})
        return True

    def fill_inventory(self, cr, uid, ids, context=False):
        res = {}
        stock_fill_inventory_obj = self.pool.get('stock.fill.inventory')
        inventory_data = self.browse(cr, uid, ids[0], context)
        if context.get('type',[]) == 'move':
            set_stock_zero = False
        else:
            set_stock_zero = True
        if inventory_data.location_id:
            context['location_id'] = inventory_data.location_id.id
            fill_inventory_id = stock_fill_inventory_obj.create(cr, uid, {
                                                                          'location_id': inventory_data.location_id.id,
                                                                          'set_stock_zero': set_stock_zero})
            context_temp = context
            context_temp['active_ids'] = [inventory_data.id]
            context_temp['active_id'] = inventory_data.id
            stock_fill_inventory_obj.fill_inventory(cr, uid, [fill_inventory_id], context_temp)


        if context.get('type',[]) == 'move':
            act = {}
#            mod_obj = self.pool.get('ir.model.data')
#            act_obj = self.pool.get('ir.actions.act_window')
#            model_id = mod_obj.search(cr, uid, [('name', '=', 'move_stock_acquisition_link_2')])[0]
#            act_id = mod_obj.read(cr, uid, model_id, ['res_id'])['res_id']
#            act = act_obj.read(cr, uid, act_id)
        else:
            mod_obj = self.pool.get('ir.model.data')
            act_obj = self.pool.get('ir.actions.act_window')
            model_id = mod_obj.search(cr, uid, [('name', '=', 'inventory_acquisition_link_1')])[0]
            act_id = mod_obj.read(cr, uid, model_id, ['res_id'])['res_id']
            act = act_obj.read(cr, uid, act_id)
            context = eval(act['context'])
            context['default_inventory_id'] = inventory_data.id
            context['default_name'] = inventory_data.name
            act['context'] = context
        return act


stock_inventory()

class stock_move(osv.osv):

    _inherit = 'stock.move'

#    def _check_move(self, cr, uid, ids, context=None):
#        """ Checks if the given production lot belong to a pack
#            Return false if the production lot is in a pack
#        """
#        production_lot_obj = self.pool.get('stock.production.lot')
#
#        for move in self.browse(cr, uid, ids, context=context):
#            if move.prodlot_id:
#               if self.search(cr, uid, [('prodlot_id', '=', move.prodlot_id.id), ('state','not in',('cancel','done')), ('id', '!=', move.id)]):
#                   if move.prodlot_id.tracking_id:
#                       return False
#        return True

    _columns = {
        'pack_history_id': fields.many2one('stock.tracking.history', 'History pack'),
    }

#    _constraints =[
#        (_check_move, 'You try to assign a move to a lot which is already in a pack', ['prodlot_id'])
#    ]
    ''' Solution to move all pack and production lot if one in a pack is move '''
#    def move_parent(self, cr, uid, ids, context=None):
#        """ Checks if the given production lot belong to a pack
#            Move the pack in the same destination
#        """
#        ''' variables '''
#        production_lot_obj = self.pool.get('stock.production.lot')
#        move_packaging_obj = self.pool.get('stock.move.packaging')
#        ''' init '''
#        if context == None:
#            context = {}
#        ''' process '''
#        for move in self.browse(cr, uid, ids, context=context):
#            if move.prodlot_id:
#               if move.prodlot_id.tracking_id:
#                   move_packaging_obj.move_pack(cr, uid, move.prodlot_id.tracking_id, context)
#        return {}

stock_move()

class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"

    _columns = {
        'date': fields.datetime('Date'),
        'note': fields.text('Notes'),
    }

stock_inventory_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
