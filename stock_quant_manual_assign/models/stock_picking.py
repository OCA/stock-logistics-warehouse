# -*- coding: utf-8 -*-
# (c) 2015 Mikel Arregi - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    picking_type_code = fields.Selection(
        related='picking_type_id.code', store=True, readonly=True)
