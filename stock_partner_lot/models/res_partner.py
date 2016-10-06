# (c) 2016 credativ ltd. - Ondřej Kuzník
# (c) 2018 Agung Rachmatullah
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
"""ResPartner addintional"""
from odoo import api, fields, models

class ResPartner(models.Model):
    """Inherit res.partner to add some fields and create
    computation of function for quant"""
    _inherit = 'res.partner'

    quant_ids = fields.One2many('stock.quant', 'owner_id',
                                string='Owned products')
    quant_count = fields.Integer('Owned Products',
                                 compute='_compute_quant_count')

    @api.multi
    def _compute_quant_count(self):
        """compute the quant each of partnet"""
        for partner in self:
            partner.quant_count = len(partner.quant_ids)
