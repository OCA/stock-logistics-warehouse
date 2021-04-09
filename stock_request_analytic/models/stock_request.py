# Copyright 2017-2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# Copyright 2021 Tecnativa - João Marques
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockRequest(models.Model):
    _inherit = "stock.request"
    _check_company_auto = True

    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account", check_company=True,
    )
    analytic_tag_ids = fields.Many2many(
        "account.analytic.tag", string="Analytic Tags", check_company=True,
    )
