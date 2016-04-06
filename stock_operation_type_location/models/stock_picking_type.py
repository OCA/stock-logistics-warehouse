# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from lxml import etree


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    allowed_location_ids = fields.Many2many(
        string='Allowed Source Location',
        comodel_name='stock.location',
        relation='picking_type_location_rel',
        column1='picking_type_id',
        column2='location_id')

    allowed_dest_location_ids = fields.Many2many(
        string='Allowed Destination Location',
        comodel_name='stock.location',
        relation='picking_type_dest_location_rel',
        column1='picking_type_id',
        column2='location_id')

    @api.model
    def fields_view_get(
        self, view_id=None, view_type='form', toolbar=False, submenu=False
    ):
        res = super(StockPickingType, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])

        for node in doc.xpath("//field[@name='allowed_location_ids']"):
            domain = "[('id', 'not in', [default_location_src_id])]"
            node.set('domain', domain)

        for node in doc.xpath("//field[@name='allowed_dest_location_ids']"):
            domain = "[('id', 'not in', [default_location_dest_id])]"
            node.set('domain', domain)

        res['arch'] = etree.tostring(doc)
        return res
