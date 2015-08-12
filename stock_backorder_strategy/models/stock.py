# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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


from openerp import api, fields, models
from openerp.tools.translate import _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _create_backorder(self, picking, backorder_moves=[]):
        res = False
        if picking.picking_type_id.backorder_strategy == 'no_create':
            res = True
        else:
            res = super(StockPicking, self)._create_backorder(
                picking, backorder_moves=backorder_moves)
            if res and picking.picking_type_id.backorder_strategy == 'cancel':
                self.browse(res).action_cancel()
        return res


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    backorder_strategy = fields.Selection(
        [('create', _('Create')), ('no_create', _('No create')),
         ('cancel', _('Cancel'))], string='Backorder Strategy',
        default='create', help="Define what to do with backorder",
        required=True)
