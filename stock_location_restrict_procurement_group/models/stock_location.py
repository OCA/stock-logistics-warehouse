# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockLocation(models.Model):

    _inherit = 'stock.location'

    group_restricted = fields.Boolean(
        'Group Restricted',
        help="Check this if you want to restrict transfers to one procurement"
        " group only")
    restricted_group = fields.Many2one(
        'procurement.group',
        compute='_compute_restricted_group',
        search='_search_restricted_group')
    restricted_group_name = fields.Char(
        related='restricted_group.name')

    def _search_restricted_group(self, operator, value):
        domain = []
        if value:
            quants = self.env['stock.quant'].search(
                [('history_ids.group_id', operator, value)])
            domain = [('id', 'in', quants.mapped('location_id.id')),
                      ('group_restricted', '=', True)]
            locations = self.search(domain)
            domain = [('id', 'in', locations._ids)]
        return domain

    @api.multi
    def _compute_restricted_group(self):
        # Looking for quants located in locations of 'group' type
        # And then look into linked moves or pack operations
        for location in self.filtered(lambda l: l.group_restricted):
            quants = self.env['stock.quant'].search(
                [('location_id', '=', location.id)])
            rest_group = quants.mapped('history_ids').filtered(
                lambda m: m.location_dest_id == location).\
                mapped('group_id')
            if not rest_group:
                rest_group = quants.mapped('history_ids').mapped(
                    'picking_id').filtered(
                    lambda p: p.pack_operation_product_ids.mapped(
                        'location_dest_id') in [location]).mapped('group_id')
            if rest_group:
                location.restricted_group = rest_group[0]
