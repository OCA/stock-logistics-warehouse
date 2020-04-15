# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class StockValuationAccountMassAdjustMove(models.TransientModel):
    _name = 'stock.valuation.account.mass.adjust.move'
    _description = 'Recreate Valuation Entries for Stock Moves'

    @api.multi
    def process(self):
        context = self.env.context
        active_model = self.env.context['active_model']
        if active_model == 'stock.move':
            moves = self.env['stock.move'].browse(
                context.get('active_ids', []))
        else:
            raise UserError(_('Incorrect model.'))

        for move in moves:
            if move.location_id.company_id == move.location_dest_id.company_id or move.state != 'done':
                # we don't want to account for internal moves or dropshipments nor for not finished moves
                continue
            account_move_lines = self.env['account.move.line'].search([('stock_move_id', '=', move.id), ('reconciled', '=', True)])
            if account_move_lines:
                # we don't want to account if the some journal entries are reconciled
                continue
            self.create_valuation_entries(move)
        action = self.env.ref('account.action_account_moves_all_a')

        result = action.read()[0]
        result['domain'] = [('stock_move_id', 'in', moves.ids)]
        return result

    def create_valuation_entries(self, move):
        # Do not create zero entries
        if not move.product_id.standard_price or move.product_qty:
            return
        # Apply restrictions on the stock move to be able to make
        # consistent accounting entries.
        if move._is_in() and move._is_out():
            raise UserError(_("The move lines are not in a consistent state: some are entering and other are leaving the company. "))
        company_src = move.mapped('move_line_ids.location_id.company_id')
        company_dst = move.mapped('move_line_ids.location_dest_id.company_id')
        try:
            if company_src:
                company_src.ensure_one()
            if company_dst:
                company_dst.ensure_one()
        except ValueError:
            raise UserError(_("The move lines are not in a consistent states: they do not share the same origin or destination company."))
        if company_src and company_dst and company_src.id != company_dst.id:
            raise UserError(_("The move lines are not in a consistent states: they are doing an intercompany in a single step while they should go through the intercompany transit location."))
        move._run_valuation()
        if move.product_id.valuation == 'real_time' and (move._is_in() or move._is_out() or move._is_dropshipped() or move._is_dropshipped_returned()):
            move._account_entry_move()
