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