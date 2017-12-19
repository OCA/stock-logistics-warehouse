# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        domain = {}
        loc = []
        dest_loc = []

        obj_stock_picking_type = self.env['stock.picking.type']

        if self.picking_type_id:
            picking_type = obj_stock_picking_type.browse(
                [self.picking_type_id.id])[0]

            allowed_location = picking_type.allowed_location_ids
            allowed_dest_location = picking_type.allowed_dest_location_ids
            scr_id = picking_type.default_location_src_id.id
            dest_id = picking_type.default_location_dest_id.id

            if allowed_location:
                for location in allowed_location:
                    loc.append(location.id)
                if scr_id and scr_id not in loc:
                    loc.append(scr_id)

            if allowed_dest_location:
                for dest_location in allowed_dest_location:
                    dest_loc.append(dest_location.id)
                if dest_id and dest_id not in dest_loc:
                    dest_loc.append(dest_id)

            if loc and dest_loc:
                domain = {
                    'location_id': [('id', 'in', loc)],
                    'location_dest_id': [('id', 'in', dest_loc)]
                }
            elif loc and not dest_loc:
                domain = {
                    'location_id': [('id', 'in', loc)],
                    'location_dest_id': []
                }
            elif not loc and dest_loc:
                domain = {
                    'location_id': [],
                    'location_dest_id': [('id', 'in', dest_loc)]
                }
            else:
                domain = {
                    'location_id': [],
                    'location_dest_id': []
                }

        return {'domain': domain}
