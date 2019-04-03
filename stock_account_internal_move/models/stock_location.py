# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    force_accounting_entries = fields.Boolean(
        string='Force accounting entries?',
    )

    @api.constrains(
        'usage',
        'force_accounting_entries',
    )
    def _check_force_accounting_entries_internal_only(self):
        for loc in self:
            if loc.usage != 'internal' and loc.force_accounting_entries:
                raise ValidationError(_(
                    'You cannot force accounting entries'
                    ' on a non-internal location.'))

    @api.constrains(
        'force_accounting_entries',
        'valuation_in_account_id',
        'valuation_out_account_id',
    )
    def _check_internal_valuation_accounts_present(self):
        """Ensure that every location requiring entries has valuation accs."""
        for loc in self:
            if loc.usage != 'internal' or not loc.force_accounting_entries:
                continue  # this one doesn't require accounts, it's fine
            if not loc.valuation_in_account_id \
                    or not loc.valuation_out_account_id:
                raise ValidationError(_(
                    'You must provide a valuation in/out account'
                    ' in order to force accounting entries.'))

    @api.onchange('usage')
    def _onchange_usage(self):
        for location in self:
            if location.usage != 'internal':
                location.update({'force_accounting_entries': False})
