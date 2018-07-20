# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools import float_round


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _action_done(self):
        res = super()._action_done()

        for move in res:
            # we're customizing behavior on moves between internal locations
            # only, thus ensuring that we don't clash w/ account moves
            # created in `stock_account`
            if not (move.location_id.usage
                    == move.location_dest_id.usage
                    == 'internal'):
                continue

            location_from = move.location_id
            location_to = move.location_dest_id

            # get valuation accounts for product
            # done in _get_accounting_data_for_valuation?
            product_valuation_accounts \
                = move.product_id.product_tmpl_id.get_product_accounts()
            stock_journal_id, __, __, __ \
                = move._get_accounting_data_for_valuation()

            # calculate move cost
            # TODO: recheck if this part respects product valuation method
            move.value = float_round(
                value=move.product_id.standard_price * move.quantity_done,
                precision_rounding=self.company_id.currency_id.rounding,
            )

            if location_from.force_accounting_entries:
                move._create_account_move_line(
                    location_from.valuation_out_internal_account_id.id,
                    product_valuation_accounts.get('stock_valuation').id,
                    stock_journal_id)

            if location_to.force_accounting_entries:
                move._create_account_move_line(
                    location_to.valuation_in_internal_account_id.id,
                    product_valuation_accounts.get('stock_valuation').id,
                    stock_journal_id)

        return res
