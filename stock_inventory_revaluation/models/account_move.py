# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, exceptions, fields, models, _


class AccountMove(models.Model):

    _inherit = 'account.move'

    stock_inventory_revaluation_id = fields.Many2one(
        comodel_name='stock.inventory.revaluation',
        string='Stock Inventory Revaluation',
        ondelete='restrict', copy=False)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.stock_inventory_revaluation_id:
                raise exceptions.Warning(
                    _("You cannot remove the journal item that is related "
                      "to an inventory revaluation"))
        return super(AccountMove, self).unlink()


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    stock_inventory_revaluation_id = fields.Many2one(
        comodel_name='stock.inventory.revaluation',
        related='move_id.stock_inventory_revaluation_id',
        string='Stock Inventory Revaluation',
        store=True, ondelete='restrict', copy=False)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.stock_inventory_revaluation_id:
                raise exceptions.Warning(
                    _("You cannot remove the journal item that is related "
                      "to an inventory revaluation"))
        return super(AccountMoveLine, self).unlink()
