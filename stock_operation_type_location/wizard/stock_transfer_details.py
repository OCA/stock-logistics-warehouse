# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from lxml import etree


class StockTransferDetails(models.TransientModel):
    _inherit = "stock.transfer_details"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(StockTransferDetails, self)\
            .fields_view_get(
                view_id=view_id, view_type=view_type,
                toolbar=toolbar, submenu=submenu)
        context = self.env.context
        loc = []
        dest_loc = []
        domain_sourceloc = "[]"
        domain_destinationloc = "[]"
        obj_stock_picking_type = self.env['stock.picking.type']

        picking_type_id = context.get('default_picking_type_id')

        if picking_type_id:
            picking_type = obj_stock_picking_type.browse(
                [picking_type_id])[0]

            allowed_location = picking_type.allowed_location_ids
            allowed_dest_location = picking_type.allowed_dest_location_ids
            src_id = picking_type.default_location_src_id.id
            dest_id = picking_type.default_location_dest_id.id

            if allowed_location:
                for location in allowed_location:
                    loc.append(location.id)
                if src_id and src_id not in loc:
                    loc.append(src_id)

            if allowed_dest_location:
                for dest_location in allowed_dest_location:
                    dest_loc.append(dest_location.id)
                if dest_id and dest_id not in dest_loc:
                    dest_loc.append(dest_id)

            if loc:
                domain_sourceloc = "[('id', 'in', %s)]" % loc
            if dest_loc:
                domain_destinationloc = "[('id', 'in', %s)]" % dest_loc

        if 'item_ids' in res['fields']:
            arch = res['fields']['item_ids'][
                'views']['tree']['arch']
            doc = etree.XML(arch)
            for node in doc.xpath("//field[@name='destinationloc_id']"):
                node.set('domain', domain_destinationloc)
            for node in doc.xpath("//field[@name='sourceloc_id']"):
                node.set('domain', domain_sourceloc)
            res['fields']['item_ids']['views'][
                'tree']['arch'] = etree.tostring(doc)

        if 'packop_ids' in res['fields']:
            arch = res['fields']['packop_ids'][
                'views']['tree']['arch']
            doc = etree.XML(arch)
            for node in doc.xpath("//field[@name='destinationloc_id']"):
                node.set('domain', domain_destinationloc)
            for node in doc.xpath("//field[@name='sourceloc_id']"):
                node.set('domain', domain_sourceloc)
            res['fields']['packop_ids']['views'][
                'tree']['arch'] = etree.tostring(doc)
        return res
