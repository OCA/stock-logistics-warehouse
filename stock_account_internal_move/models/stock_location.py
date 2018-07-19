# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    _sql_constraints = [
        ('valuation_account_present',
         # ensures that there's always a valuation account present
         # when account entries on it are forced
         """check(
         NOT force_accounting_entries
         OR force_accounting_entries
         AND valuation_internal_account_id IS NOT NULL)""",
         'You must provide a valuation account to force accounting entries.'),
    ]

    # both used only for usage == internal
    valuation_internal_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Valuation Account (internal transfers)',
    )
    force_accounting_entries = fields.Boolean(
        string='Force accounting entries?',
    )
