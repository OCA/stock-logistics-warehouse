# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Alex Duan <alex.duan@elico-corp.com>, Liu Lixia<liu.lixia@elico-corp.com>
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
from openerp.osv import orm, fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    def _kits_product_available(self, cr, uid, ids, field_names=None,
                                arg=False, context=None):
        res = {}
        field_names = field_names or []
        context = context or {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
        field_map = {
            'kits_qty_available': 'qty_available',
            'kits_incoming_qty': 'incoming_qty',
        }
        for product_record in self.browse(cr, uid, ids, context=context):
            # check if is a kit product.
            so_qty = self._get_sale_quotation_qty(cr, uid, product_record.id,
                                                  context=context)
            if not self._is_kit(
                cr, uid,
                [product_record.id],
                    context=context).get(product_record.id):

                res[product_record.id] = {
                    'kits_qty_available': 0,
                    'kits_incoming_qty': 0,
                    'kits_sale_quotation_qty': so_qty
                }
            else:
                flag = True
                for bom in product_record.bom_ids:
                    """ now get always get the default_for_kit of bom is \
                        True and bom type is phantom."""
                    if bom.default_for_kit and bom.type == 'phantom':
                        child_product_res = {}
                        for line in bom.bom_lines:
                            child_product_res[line.product_id.id] = {
                                'product_qty': line.product_qty or 0.0,
                                'product_uom': line.product_uom,
                                'uom': bom.product_id.uom_id,
                                'mrp_product_qty': line.bom_id.product_qty,
                                'mrp_product_uom': line.bom_id.product_uom}
                        child_product_qtys = self._product_available(
                            cr, uid, child_product_res.keys(),
                            field_map.values(), context=context)
                        res[product_record.id] = {
                            'kits_qty_available': self._get_qty_from_children(
                                cr, uid, child_product_qtys, child_product_res,
                                'qty_available'),
                            'kits_incoming_qty': self._get_qty_from_children(
                                cr, uid, child_product_qtys, child_product_res,
                                'incoming_qty'),
                            'kits_sale_quotation_qty': so_qty
                        }
                        flag = False
                        break
                if flag:
                    for bom in product_record.bom_ids:
                        if not bom.default_for_kit and bom.type == 'phantom':
                            child_product_res = {}
                            for line in bom.bom_lines:
                                child_product_res[line.product_id.id] = {
                                    'product_qty': line.product_qty or 0.0,
                                    'product_uom': line.product_uom,
                                    'uom': bom.product_id.uom_id,
                                    'mrp_product_qty': line.bom_id.product_qty,
                                    'mrp_product_uom': line.bom_id.product_uom
                                }
                            child_product_qtys = self._product_available(
                                cr, uid, child_product_res.keys(),
                                field_map.values(), context=context)
                            res[product_record.id] = {
                                'kits_qty_available':
                                self._get_qty_from_children(
                                    cr, uid, child_product_qtys,
                                    child_product_res,
                                    'qty_available'),
                                'kits_incoming_qty':
                                self._get_qty_from_children(
                                    cr, uid, child_product_qtys,
                                    child_product_res,
                                    'incoming_qty'),
                                'kits_sale_quotation_qty': so_qty
                            }
                            break
                        else:
                            raw_res = self._product_available(
                                cr, uid, ids, field_map.values(), arg, context)
                            for key, val in field_map.items():
                                res[product_record.id][key] = \
                                    raw_res[product_record.id].get(val)
        return res

    def _product_available(self, cr, uid, ids, field_names=None,
                           arg=False, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values which contain product_uom.
        """
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
        for f in field_names:
            c = context.copy()
            if f == 'qty_available':
                c.update({'states': ('done',), 'what': ('in', 'out')})
            if f == 'virtual_available':
                c.update({'states': ('confirmed', 'waiting', 'assigned',
                          'done'), 'what': ('in', 'out')})
            if f == 'incoming_qty':
                c.update({'states': ('confirmed', 'waiting', 'assigned'),
                          'what': ('in',)})
            if f == 'outgoing_qty':
                c.update({'states': ('confirmed', 'waiting', 'assigned'),
                          'what': ('out',)})
            stock = self.get_product_available(cr, uid, ids, context=c)
            for id in ids:
                res[id][f] = stock.get(id, 0.0)
                product_obj = self.pool['product.product'].browse(cr, uid, id)
                res[id]['product_uom'] = product_obj.uom_id
        return res

    # get sale quotation of this product.
    def _get_sale_quotation_qty(self, cr, uid, product_id, context=None):
        '''get all qty of the product in all sale quotations (draft, sent)'''
        total = 0.0
        sol_obj = self.pool['sale.order.line']
        product_uom_obj = self.pool['product.uom']
        domain = [('state', 'in', ('draft', False, None)),
                  ('product_id', '=', product_id)]
        sol_ids = sol_obj.search(cr, uid, domain)
        for sol_id in sol_ids:
            solobj = sol_obj.browse(cr, uid, sol_id)
            if not solobj.product_id:
                continue
            total += product_uom_obj._compute_qty(cr, uid,
                                                  solobj.product_uom.id,
                                                  solobj.product_uom_qty,
                                                  solobj.product_id.uom_id.id)
        return total

    def _get_qty_from_children(
            self, cr, uid, child_product_qtys, child_product_res, field_name):
        def qty_div(product_total_qty, component_qty):
            product_uom_obj = self.pool['product.uom']
            kit_number = product_uom_obj._compute_qty(
                cr, uid, component_qty[1]['mrp_product_uom'].id,
                component_qty[1]['mrp_product_qty'],
                component_qty[1]['uom'].id)
            amout = product_uom_obj._compute_qty(
                cr, uid, component_qty[1]['product_uom'].id,
                component_qty[1]['product_qty'],
                component_qty[1]['uom'].id)
            com_number = amout / kit_number
            com_total = product_uom_obj._compute_qty(
                cr, uid, product_total_qty[1]['product_uom'].id,
                product_total_qty[1].get(field_name),
                component_qty[1]['uom'].id)
            number = com_total / com_number
            return int(number)

        # when the bom has no components
        if not child_product_res:
            return 0
        return min(map(qty_div, child_product_qtys.iteritems(),
                   child_product_res.iteritems()))

    def _is_kit(self, cr, uid, ids, fields=None, args=False, context=None):
        '''see if this product is Kit or not'''
        res = {}
        for product_record in self.browse(cr, uid, ids, context=context):
            res[product_record.id] = False
            if product_record.bom_ids:
                for bom in product_record.bom_ids:
                    if bom.type == 'phantom':
                        res[product_record.id] = True
        return res

    def _get_product_from_bom(self, cr, uid, ids, context=None):
        res = {}
        bom_ids = self.pool.get('mrp.bom').browse(
            cr, uid, ids, context=context)
        for bom in bom_ids:
            res[bom.product_id.id] = True
        return res.keys()

    _columns = {
        'is_kit': fields.function(
            _is_kit,
            readonly=True,
            type='boolean',
            string='Is Kit',
            store={
                'mrp.bom': (_get_product_from_bom, ['type', 'company_id'], 10)
            }),
        'kits_qty_available': fields.function(
            _kits_product_available,
            multi='kits_qty_available',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quantity On Hand (Kits)',
            help=""),
        'kits_incoming_qty': fields.function(
            _kits_product_available,
            multi='kits_qty_available',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Incoming (Kits)',
            help=""),
        'kits_sale_quotation_qty': fields.function(
            _kits_product_available,
            multi='kits_qty_available',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Sales Quotation Allocated',
            help=""),
    }


class MrpBom(orm.Model):

    _inherit = 'mrp.bom'

    _columns = {
        'default_for_kit': fields.boolean(
            string='Default For Kit'), }

    _defaults = {
        'default_for_kit': False
    }

    def create(self, cr, uid, vals, context=None):
        result = True
        if vals.get('type') == 'phantom' and vals.get('default_for_kit'):
            bom_obj = self.pool['mrp.bom']
            domain = [('product_id', '=', vals['product_id'])]
            bom_ids = bom_obj.search(cr, uid, domain)
            for bom_id in bom_ids:
                mrpbom_obj = bom_obj.browse(cr, uid, bom_id)
                if mrpbom_obj.default_for_kit:
                    result = False
                    break
        if not result:
            raise osv.except_osv(_('Warning!'), _('More bom of the kit product \
                set default.\nPlease set one or we cannot automatically \
                calculate for kits product.'))
        return super(MrpBom, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        result = True
        bom_pool = self.pool['mrp.bom']
        bom_obj = bom_pool.browse(cr, uid, ids, context=context)[0]
        flag = False
        if 'type' in vals and vals['type'] == 'phantom' and 'default_for_kit' \
                in vals and vals['default_for_kit']:
            flag = True
        elif 'type' in vals and vals['type'] == 'phantom' and 'default_for_kit' \
                not in vals and bom_obj.default_for_kit:
            flag = True
        elif 'type' not in vals and 'default_for_kit' not in vals and bom_obj.type \
                == 'phantom' and bom_obj.default_for_kit:
            flag = True
        elif 'type' not in vals and 'default_for_kit' in vals and \
                vals['default_for_kit']:
            flag = True
        if flag:
            if 'product_id' in vals:
                product_id = vals['product_id']
            else:
                product_id = bom_obj.product_id.id
            domain = [('product_id', '=', product_id)]
            bom_ids = self.pool['mrp.bom'].search(cr, uid, domain,
                                                  context=context)
            for bom_id in bom_ids:
                mrpbom_obj = bom_pool.browse(cr, uid, bom_id,
                                             context=context)
                if mrpbom_obj.default_for_kit and mrpbom_obj.id != bom_obj.id:
                    result = False
                    break
        if not result:
            raise osv.except_osv(_('Warning!'), _('More bom of the kit product \
                set default.\nPlease set one or we cannot automatically \
                calculate for kits product.'))
        return super(MrpBom, self).write(cr, uid, ids, vals, context=context)
