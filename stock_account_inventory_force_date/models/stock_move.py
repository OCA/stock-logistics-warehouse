# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# Copyright 2019 Aleph Objects, Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_round


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_valued_quantity(self):
        valued_move_lines = self.env['stock.move.line']
        if self._is_in():
            valued_move_lines = self.move_line_ids.filtered(
                lambda ml: not ml.location_id._should_be_valued() and
                ml.location_dest_id._should_be_valued() and
                not ml.owner_id)
        elif self._is_out():
            valued_move_lines = self.move_line_ids.filtered(
                lambda ml: ml.location_id._should_be_valued() and not
                ml.location_dest_id._should_be_valued() and not ml.owner_id)
        valued_quantity = 0
        for valued_move_line in valued_move_lines:
            valued_quantity += \
                valued_move_line.product_uom_id._compute_quantity(
                    valued_move_line.qty_done, self.product_id.uom_id)
        return valued_quantity

    def _prepare_move_price_history(self, history, diff):
        valued_quantity = self._get_valued_quantity()
        account_id = self.company_id.standard_cost_change_account_id.id
        if not account_id:
            raise ValidationError(_(
                'Please define a Standard Cost Change Offsetting Account '
                'in the company settings.'))
        # Accounting Entries
        product = self.product_id
        product_accounts = product.product_tmpl_id.get_product_accounts()
        if diff * valued_quantity < 0:
            debit_account_id = account_id
            credit_account_id = product_accounts['stock_valuation'].id
        else:
            debit_account_id = product_accounts['stock_valuation'].id
            credit_account_id = account_id
        description = _('Standard Price revalued for %s from %s') % (
            self.product_id.display_name, self.inventory_id.name)
        move_vals = {
            'journal_id': product_accounts['stock_journal'].id,
            'company_id': self.company_id.id,
            'date': history.datetime,
            'stock_move_id': self.id,
            'line_ids': [(0, 0, {
                'name': description,
                'account_id': debit_account_id,
                'debit': abs(diff * valued_quantity),
                'credit': 0,
                'product_id': self.product_id.id,
            }), (0, 0, {
                'name': description,
                'account_id': credit_account_id,
                'debit': 0,
                'credit': abs(diff * valued_quantity),
                'product_id': self.product_id.id,
            })],
        }
        return move_vals

    def _create_move_price_history(self, history, old_cost):
        diff = history.cost - old_cost
        if not diff:
            return
        move_vals = self._prepare_move_price_history(history, diff)
        move = self.env['account.move'].create(move_vals)
        move.post()

    @api.multi
    def _replay_product_price_history_moves(self, forced_inventory_date):
        recs = self.env['product.price.history'].search([
            ('product_id', '=', self.product_id.id),
            ('company_id', '=', self.company_id.id),
            ('datetime', '>', forced_inventory_date),
        ], order="datetime asc")
        old_cost = self.price_unit
        for rec in recs:
            self._create_move_price_history(rec, old_cost)
            old_cost = rec.cost

    def _run_valuation(self, quantity=None):
        forced_inventory_date = self.env.context.get(
            'forced_inventory_date', False)
        super(StockMove, self)._run_valuation(quantity=quantity)
        valued_quantity = self._get_valued_quantity()
        if self.product_id.cost_method == 'standard' and forced_inventory_date:
            price_used = self.product_id.get_history_price(
                self.env.user.company_id.id,
                date=forced_inventory_date,
            )
            curr_rounding = self.company_id.currency_id.rounding
            value = float_round(price_used * (quantity or valued_quantity),
                                precision_rounding=curr_rounding)
            if valued_quantity:
                price_unit = value / valued_quantity
            elif quantity:
                price_unit = value / quantity
            else:
                price_unit = 0.0
            if self._is_out() or self._is_dropshipped_returned():
                value *= -1
                price_unit *= -1
            self.write({
                'value': value,
                'price_unit': price_unit,
            })

    @api.multi
    def _action_done(self):
        moves = super(StockMove, self)._action_done()
        forced_inventory_date = self.env.context.get(
            'forced_inventory_date', False)
        if forced_inventory_date:
            moves.write({'date': forced_inventory_date})
            for move in moves.filtered(
                lambda m: m.product_id.valuation == 'real_time' and (
                    m._is_in() or m._is_out() or m._is_dropshipped() or
                    m._is_dropshipped_returned())):
                move._replay_product_price_history_moves(
                    forced_inventory_date)
        return moves
