# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    stock_request_ids = fields.One2many(
        comodel_name='stock.request', inverse_name='analytic_account_id',
        string='Stock Requests', copy=False)
