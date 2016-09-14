# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    dest_partner_id = fields.Many2one(
        comodel_name='res.partner', compute='_compute_partner_id',
        string='Partner', store=True)

    @api.depends('location_id', 'history_ids')
    def _compute_partner_id(self):
        for quant in self.filtered(
                lambda q: q.location_id.usage in ['customer', 'supplier']):
            move = quant.history_ids[:-1]
            quant.dest_partner_id =\
                move.picking_id.partner_id.commercial_partner_id
