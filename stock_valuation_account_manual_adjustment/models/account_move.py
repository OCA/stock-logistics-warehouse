# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class AccountMove(models.Model):

    _inherit = 'account.move'

    stock_valuation_account_manual_adjustment_id = fields.Many2one(
        comodel_name='account.inventory.adjustment',
        string='Stock Valuation Account Manual Adjustment',
        ondelete='restrict')


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    stock_valuation_account_manual_adjustment_id = fields.Many2one(
        related='move_id.stock_valuation_account_manual_adjustment_id',
        string='Stock Valuation Account Manual Adjustment',
        store=True, ondelete='restrict')
