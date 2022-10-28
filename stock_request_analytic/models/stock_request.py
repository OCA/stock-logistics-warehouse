# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockRequest(models.Model):
    _inherit = "stock.request"

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account')

    @api.constrains('analytic_account_id')
    def _check_analytic_company_constrains(self):
        if any(r.company_id and r.analytic_account_id and
               r.analytic_account_id.company_id != r.company_id for r in self):
                raise ValidationError(
                    _('You cannot link a analytic account '
                      'to a stock request that belongs to '
                      'another company.'))
