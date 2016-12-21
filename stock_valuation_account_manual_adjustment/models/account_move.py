# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, exceptions, fields, models, _


class AccountMove(models.Model):

    _inherit = 'account.move'

    stock_valuation_account_manual_adjustment_id = fields.Many2one(
        comodel_name='stock.valuation.account.manual.adjustment',
        string='Stock Valuation Account Manual Adjustment',
        ondelete='restrict')

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.stock_valuation_account_manual_adjustment_id:
                raise exceptions.Warning(
                    _("You cannot remove the journal entry that is related "
                      "to a Stock valuation account manual adjustment "))
        return super(AccountMove, self).unlink()


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    stock_valuation_account_manual_adjustment_id = fields.Many2one(
        comodel_name='stock.valuation.account.manual.adjustment',
        related='move_id.stock_valuation_account_manual_adjustment_id',
        string='Stock Valuation Account Manual Adjustment',
        store=True, ondelete='restrict')

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.stock_valuation_account_manual_adjustment_id:
                raise exceptions.Warning(
                    _("You cannot remove the journal item that is related "
                      "to a Stock valuation account manual adjustment "))
        return super(AccountMoveLine, self).unlink()
