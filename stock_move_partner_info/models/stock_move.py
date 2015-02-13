# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    picking_partner = fields.Many2one(
        'res.partner', string='Picking Partner', store=True,
        related='picking_id.partner_id', help='Partner of the picking')
