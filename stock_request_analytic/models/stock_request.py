# Copyright 2017-2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockRequest(models.Model):
    _inherit = "stock.request"
    _check_company_auto = True

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        compute="_compute_analytic_id",
        store=True,
        readonly=False,
        check_company=True,
        compute_sudo=True,
    )
    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
        check_company=True,
    )

    @api.depends("order_id")
    def _compute_analytic_id(self):
        """
        Set default analytic account on lines from order if defined.
        """
        for req in self:
            if req.order_id and req.order_id.default_analytic_account_id:
                req.analytic_account_id = req.order_id.default_analytic_account_id

    def _prepare_procurement_values(self, group_id=False):
        """
        Add analytic account to procurement values
        """
        res = super()._prepare_procurement_values(group_id=group_id)
        if self.analytic_account_id:
            res.update({"analytic_account_id": self.analytic_account_id.id})
        return res
