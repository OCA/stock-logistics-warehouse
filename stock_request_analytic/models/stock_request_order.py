# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    analytic_count = fields.Integer(
        compute="_compute_analytic_ids",
        readonly=True,
        compute_sudo=True,
    )
    analytic_account_ids = fields.One2many(
        comodel_name="account.analytic.account",
        compute="_compute_analytic_ids",
        string="Analytic Accounts",
        readonly=True,
        compute_sudo=True,
    )
    default_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Default Analytic Account",
        help="Set this if you want to define a default analytic account on requests",
    )

    @api.depends("stock_request_ids")
    def _compute_analytic_ids(self):
        for req in self:
            analytic_account_ids = set()
            for distribution in req.stock_request_ids.mapped("analytic_distribution"):
                if not distribution:
                    continue
                for key in distribution.keys():
                    try:
                        analytic_account_ids.add(int(key))
                    except (TypeError, ValueError):
                        continue
            req.analytic_account_ids = self.env["account.analytic.account"].browse(
                list(analytic_account_ids)
            )
            req.analytic_count = len(req.analytic_account_ids)

    def action_view_analytic(self):
        self.ensure_one()
        analytic_type = self.env.context.get("analytic_type")
        if not analytic_type or analytic_type != "analytic_account":
            raise ValidationError(
                _("Analytic type (analytic_type) not present in the context")
            )
        records = self.analytic_account_ids
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "analytic.action_account_analytic_account_form"
        )
        if len(records) > 1:
            action["domain"] = [("id", "in", records.ids)]
        elif records:
            action["views"] = [
                (
                    self.env.ref("analytic.view_account_analytic_account_form").id,
                    "form",
                )
            ]
            action["res_id"] = records.id
        return action
