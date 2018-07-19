# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _action_done(self):
        res = super()._action_done()
        for move in self:
            if not (move.location_id.usage == 'internal'
                    and move.location_dest_id.usage == 'internal'):
                continue

            location_src = move.location_id
            location_dest = move.location_dest_id
            if location_src.force_accounting_entries \
                    != location_dest.force_accounting_entries:
                raise ValidationError(_(
                    'Could not generate a journal entry.'
                    ' You need to either force or disable accounting on both'
                    ' locations in order to do that.'))
            if not location_src.force_accounting_entries:
                # `force_accounting_entries` is the same as on dest location
                continue

            # checks above along w/ the constraint ensuring the presence of
            # valuation accounts on both src and dest locations
            outgoing_acc = move.location_id.valuation_internal_account_id
            receiving_acc = move.location_dest_id.valuation_internal_account_id
            # return journal_id, acc_src, acc_dest, acc_valuation
            journal_id, acc_src_id, acc_dest_id, acc_valuation \
                = move._get_accounting_data_for_valuation()
            move._create_account_move_line(
                outgoing_acc, receiving_acc, journal_id)
        return res
