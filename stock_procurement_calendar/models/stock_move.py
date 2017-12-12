# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
# from odoo.osv import expression


class StockMove(models.Model):

    _inherit = 'stock.move'

    # TODO: Assignation and grouping  # pylint: disable=W0511
    '''
    @api.model
    def _get_picking_assign_domain(self, move):
        domain = super(StockMove, self)._get_picking_assign_domain()
        if move.procurement_id and\
                move.procurement_id.procurement_location_calendar_id:
            domain = expression.AND([
                [('')]
            ])
    '''
