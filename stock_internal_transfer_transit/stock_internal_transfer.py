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


from openerp.osv import orm
from openerp.netsvc import LocalService


class StockInternalTransfer(orm.TransientModel):
    _inherit = 'stock.internal.transfer'

    def _prepare_picking(self, cr, uid, ids, context=None):
        assert len(ids) == 1,\
            'This function should only be used for a single id at a time.'

        picking_data = super(StockInternalTransfer, self).\
            _prepare_picking(cr, uid, ids, context=context)
        wiz = self.browse(cr, uid, ids[0], context=context)

        if wiz.mode == 'force':
            return picking_data

        # update destination location to transfer using
        # intermediate transit stock location
        model_data_obj = self.pool['ir.model.data']
        stock_loc_transit_id = model_data_obj.\
            get_object_reference(cr, uid, 'stock_internal_transfer_transit',
                                 'stock_location_transit')[1]

        picking_data.update({'location_dest_id': stock_loc_transit_id, })
        return picking_data

    def _show_picking(self, picking_ids):
        act_data = super(StockInternalTransfer, self).\
            _show_picking(picking_ids)
        act_data.update({
            'domain': [('id', 'in', picking_ids)],
            'view_mode': 'tree,form',
        })
        return act_data

    def _create_transfer(self, cr, uid, ids, context=None):
        assert len(ids) == 1,\
            'This function should only be used for a single id at a time.'
        wiz = self.browse(cr, uid, ids[0], context=context)
        picking_model = self.pool['stock.picking']

        # create 1st picking: src loc -> transit loc
        src2transit_id = super(StockInternalTransfer, self).\
            _create_transfer(cr, uid, ids, context=context)[0]
        src2transit = picking_model.\
            browse(cr, uid, src2transit_id, context=context)

        res_ids = [src2transit_id]

        # check if transit loc is used in transfer
        # create 2nd picking: transit loc -> dest loc
        if wiz.location_dest_id.id != src2transit.location_dest_id.id:
            picking_data = self._prepare_picking(cr, uid, ids, context=context)
            picking_data.update({
                'location_id': src2transit.location_dest_id.id,
                'location_dest_id': wiz.location_dest_id.id,
            })

            transit2dst_id = picking_model.\
                create(cr, uid, picking_data, context=context)
            transit2dst = picking_model.\
                browse(cr, uid, transit2dst_id, context=context)

            move_obj = self.pool['stock.move']

            for move in src2transit.move_lines:
                new_id = move_obj.copy(cr, uid, move.id, {
                    'location_id': transit2dst.location_id.id,
                    'location_dest_id': transit2dst.location_dest_id.id,
                    'picking_id': transit2dst.id,
                    'state': 'waiting',
                    'move_history_ids': [],
                    'move_history_ids2': []}
                )
                # chain moves
                move.write({
                    'move_dest_id': new_id,
                    'move_history_ids': [(4, new_id)]
                })

            wf_service = LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking',
                                    transit2dst_id, 'button_confirm', cr)
            # picking_model.action_assign(cr, uid, [transit2dst_id])
            res_ids.append(transit2dst_id)

        return res_ids
