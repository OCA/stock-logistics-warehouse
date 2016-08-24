# -*- coding: utf-8 -*-

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    quant_ids = fields.One2many('stock.quant', 'owner_id',
                                string='Owned products')
    quant_count = fields.Integer('Owned Products',
                                 compute='_compute_quant_count')

    @api.multi
    def _compute_quant_count(self):
        for partner in self:
            partner.quant_count = len(partner.quant_ids)
