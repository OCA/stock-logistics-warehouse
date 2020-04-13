# -*- coding: utf-8 -*-
# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class StockValuationAccountMassAdjustPicking(models.TransientModel):
    _name = 'stock.valuation.account.mass.adjust.picking'
    _description = 'Recreate Valuation Entries for Pickings'


    @api.multi
    def process(self):
        context = self.env.context
        active_model = self.env.context['active_model']
        if active_model == 'stock.picking':
            pickings = self.env['stock.picking'].browse(
                context.get('active_ids', []))
        else:
            raise UserError(_('Incorrect model.'))

        for picking in pickings:
            if picking.location_id.company_id == picking.location_dest_id.company_id or picking.state != 'done':
                # we don't want to account for internal moves or dropshipments nor for not finished pickings
                continue
            self.create_valuation_entries(picking)
        action = self.env.ref('account.action_account_moves_all_a')

        result = action.read()[0]
        result['domain'] = [('stock_move_id', 'in', pickings.mapped('move_lines').ids)]
        return result

    def create_valuation_entries(self, picking):
        for move in picking.move_lines:
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
        for move in picking.move_lines.filtered(lambda m: m.product_id.valuation == 'real_time' and (m._is_in() or m._is_out() or m._is_dropshipped() or m._is_dropshipped_returned())):
            move._account_entry_move()
