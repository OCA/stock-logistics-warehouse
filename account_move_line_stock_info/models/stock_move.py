# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    account_move_line_ids = fields.One2many(
        comodel_name='account.move.line', inverse_name='stock_move_id',
        copy=False)
