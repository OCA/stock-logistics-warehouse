# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPackOperation(models.Model):

    _inherit = 'stock.pack.operation'

    restricted = fields.Boolean(
        compute='_compute_restricted')

    @api.multi
    def restricted_op(self):
        return False

    @api.multi
    @api.depends('location_dest_id.restricted_group')
    def _compute_restricted(self):
        for op in self:
            if op.location_dest_id and\
                    op.location_dest_id.restricted_group and\
                    op.picking_id.group_id != op.location_dest_id.\
                    restricted_group:
                op.restricted = True
            else:
                op.restricted = False
