# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    dest_partner_id = fields.Many2one(
        comodel_name='res.partner', compute='_compute_partner_id',
        string='Partner', store=True)

    @api.depends('history_ids.picking_id.partner_id.commercial_partner_id',
                 'history_ids.location_id.usage',
                 'history_ids.date')
    def _compute_partner_id(self):
        for quant in self:
            moves = quant.history_ids.sorted(key=lambda m: m.date)
            dest_partner = False
            if moves:
                move = moves[-1]
                if move.location_id.usage in ('customer', 'supplier'):
                    picking = move.picking_id
                    dest_partner = picking.partner_id.commercial_partner_id
            quant.dest_partner_id = dest_partner
