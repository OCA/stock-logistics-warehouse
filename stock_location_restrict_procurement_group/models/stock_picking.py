# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        for picking in self:
            restr_location = picking.pack_operation_ids.mapped(
                'location_dest_id').filtered(lambda l: l.restricted_group)
            if restr_location and picking.group_id !=\
                    restr_location.restricted_group:
                raise UserError(_('The destination location (%s) is '
                                  'restricted to operation for the '
                                  'procurement group %s.\n'
                                  'Please choose another destination.'
                                  % (restr_location.name,
                                     restr_location.restricted_group.name)))
        return super(StockPicking, self).do_new_transfer()
