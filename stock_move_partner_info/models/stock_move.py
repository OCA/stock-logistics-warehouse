# -*- coding: utf-8 -*-
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    picking_partner = fields.Many2one(
        'res.partner', string='Picking Partner', store=True,
        related='picking_id.partner_id', help='Partner of the picking')
