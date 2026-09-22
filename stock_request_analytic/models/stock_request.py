# Copyright 2017-2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockRequest(models.Model):
    _name = "stock.request"
    _inherit = ["stock.request", "analytic.mixin"]
    _check_company_auto = True

    @api.depends("order_id.default_analytic_account_id")
    def _compute_analytic_distribution(self):
        for req in self:
            default_account = req.order_id.default_analytic_account_id
            if not req.analytic_distribution and default_account:
                req.analytic_distribution = {str(default_account.id): 100}
            else:
                req.analytic_distribution = req.analytic_distribution
