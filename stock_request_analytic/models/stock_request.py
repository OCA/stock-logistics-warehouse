# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockRequest(models.Model):
    _inherit = "stock.request"

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account')

    @api.constrains('analytic_account_id')
    def _check_analytic_company_constrains(self):
        if any(request.company_id and
               request.analytic_account_id.company_id !=
               request.company_id for request in self):
                raise ValidationError(
                    _('You cannot link a analytic account '
                      'to a stock request that belongs to '
                      'another company.'))
