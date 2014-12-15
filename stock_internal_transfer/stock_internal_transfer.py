# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
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


from openerp.osv import orm, fields
from openerp.netsvc import LocalService
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class stock_internal_transfer_line(orm.TransientModel):
    _name = "stock.internal.transfer.line"
    _rec_name = 'product_id'
    _columns = {
        'product_id': fields.many2one('product.product', string="Product",
                                      required=True, ondelete='CASCADE'),
        'quantity': fields.float(
            "Quantity",
            digits_compute=dp.get_precision('Product Unit of Measure'),
            required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure',
                                       required=True, ondelete='CASCADE'),
        'wizard_id': fields.many2one('stock.internal.transfer',
                                     string="Wizard", ondelete='CASCADE'),
    }

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        uom_id = False
        if product_id:
            product = self.pool['product.product'].\
                browse(cr, uid, product_id, context=context)
            uom_id = product.uom_id.id
        return {'value': {'product_uom': uom_id}}


class stock_internal_transfer(orm.TransientModel):
    _name = 'stock.internal.transfer'

    def _get_transfer_mode_sel(self, cr, uid, context=None):
        return [('default', _('Default')), ('force', _('Force Transfer'))]

    _columns = {
        'location_id': fields.many2one(
            'stock.location', string="Location", required=True,
            ondelete='CASCADE', domain=[('usage', '<>', 'view')]),
        'location_dest_id': fields.many2one(
            'stock.location', string="Dest. Location", required=True,
            ondelete='CASCADE', domain=[('usage', '<>', 'view')]),
        'delivery_partner_id': fields.many2one(
            'res.partner', string="Delivery Address", required=True),
        'line_ids': fields.one2many(
            'stock.internal.transfer.line', 'wizard_id', 'Move Lines'),
        'mode': fields.selection(
            lambda self, *a, **kw:
            self._get_transfer_mode_sel(*a, **kw), string="Transfer Mode", ),
    }

    _defaults = {
        'mode': 'default',
    }

    def onchange_location_dest_id(self, cr, uid, ids, location_dest_id,
                                  context=None):
        if location_dest_id:
            location = self.pool['stock.location'].\
                browse(cr, uid, location_dest_id, context=context)
            return {'value': {'delivery_partner_id': location.partner_id.id}}
        return {}

    def _prepare_picking(self, cr, uid, ids, context=None):
        assert len(ids) == 1, \
            'This function should only be used for a single id at a time.'

        wiz = self.browse(cr, uid, ids[0], context=context)
        picking_data = {
            'type': 'internal',
            'origin': _('Internal Transfer Wizard'),
            'location_id': wiz.location_id.id,
            'location_dest_id': wiz.location_dest_id.id,
            'partner_id': wiz.delivery_partner_id.id,
            # we require all products to be available for shipment
            'move_type': 'one',
        }
        return picking_data

    def _create_move_lines(self, cr, uid, ids, picking_id, context=None):
        assert len(ids) == 1, \
            'This function should only be used for a single id at a time.'
        move_obj = self.pool['stock.move']
        picking_model = self.pool['stock.picking']

        wizard = self.browse(cr, uid, ids[0], context=context)
        picking = picking_model.browse(cr, uid, picking_id, context=context)

        for line in wizard.line_ids:
            # todo move to _prepare function
            move_data = {
                'product_id': line.product_id.id,
                'product_qty': line.quantity,
                'product_uom': line.product_uom.id,
                'picking_id': picking.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'name': line.product_id.name_get()[0][1],
            }
            move_obj.create(cr, uid, move_data, context=context)

    def _create_transfer(self, cr, uid, ids, context=None):
        assert len(ids) == 1, \
            'This function should only be used for a single id at a time.'
        picking_obj = self.pool['stock.picking']

        picking_data = self._prepare_picking(cr, uid, ids, context=context)
        picking_id = picking_obj.create(cr, uid, picking_data, context=context)
        self._create_move_lines(cr, uid, ids, picking_id, context=context)

        wf_service = LocalService("workflow")
        wf_service.trg_validate(uid, 'stock.picking',
                                picking_id, 'button_confirm', cr)
        picking_id = [picking_id]
        picking_obj.action_assign(cr, uid, picking_id)
        return picking_id

    def _trigger_workflow_for_delivery(self, cr, uid, ids, picking_ids,
                                       context=None):
        wf_service = LocalService("workflow")
        for id in picking_ids:
            wf_service.trg_validate(uid, 'stock.picking',
                                    id, 'button_done', cr)

    def _show_picking(self, picking_ids):
        return {
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_id': picking_ids[0],
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def create_transfer(self, cr, uid, ids, context=None):
        assert len(ids) == 1, \
            'This function should only be used for a single id at a time.'
        wiz = self.browse(cr, uid, ids[0], context=context)
        picking_obj = self.pool['stock.picking']

        picking_ids = self._create_transfer(cr, uid, ids, context=context)
        if wiz.mode in ['force']:
            picking_obj.force_assign(cr, uid, picking_ids)
            self._trigger_workflow_for_delivery(cr, uid, ids,
                                                picking_ids, context=context)

        return self._show_picking(picking_ids)
