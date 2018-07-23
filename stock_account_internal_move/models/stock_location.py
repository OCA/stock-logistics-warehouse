# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    _sql_constraints = [
        ('valuation_account_present',
         # ensures that there's always a pair of valuation accounts present
         # when account entries on it are forced
         """check(
            NOT force_accounting_entries
            OR force_accounting_entries
            AND valuation_out_internal_account_id IS NOT NULL
            AND valuation_in_internal_account_id IS NOT NULL
         )""",
         _('You must provide a valuation in/out accounts'
           ' in order to force accounting entries.')),
        ('force_accounting_entries_internal_only',
         """check(
            NOT force_accounting_entries
            OR force_accounting_entries
            AND usage = 'internal')""",
         _('You cannot force accounting entries on a non-internal locations.')),
    ]

    force_accounting_entries = fields.Boolean(
        string='Force accounting entries?',
    )
    # both used only for usage == internal
    valuation_in_internal_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Stock Valuation Account (incoming)',
    )
    valuation_out_internal_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Stock Valuation Account (outgoing)',
    )

    @api.onchange('usage')
    def _onchange_usage(self):
        for location in self:
            if location.usage != 'internal':
                location.update({'force_accounting_entries': False})
