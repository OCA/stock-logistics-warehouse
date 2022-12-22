# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

MAP_ACTIONS = {
    "analytic_account": "analytic.action_account_analytic_account_form",
    "analytic_tag": "analytic.account_analytic_tag_action",
}
MAP_FIELDS = {
    "analytic_account": "analytic_account_ids",
    "analytic_tag": "analytic_tag_ids",
}
MAP_VIEWS = {
    "analytic_account": "analytic.view_account_analytic_account_form",
    "analytic_tag": "analytic.account_analytic_tag_form_view",
}


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    analytic_count = fields.Integer(
        compute="_compute_analytic_ids",
        readonly=True,
        compute_sudo=True,
    )
    analytic_tag_count = fields.Integer(
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
    analytic_tag_ids = fields.One2many(
        comodel_name="account.analytic.tag",
        compute="_compute_analytic_ids",
        string="Analytic Tags",
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
            req.analytic_account_ids = req.stock_request_ids.mapped(
                "analytic_account_id"
            )
            req.analytic_tag_ids = req.stock_request_ids.mapped("analytic_tag_ids")
            req.analytic_count = len(req.analytic_account_ids)
            req.analytic_tag_count = len(req.analytic_tag_ids)

    def action_view_analytic(self):
        self.ensure_one()
        analytic_type = self.env.context.get("analytic_type")
        if not analytic_type:
            raise ValidationError(
                _("Analytic type (analytic_type) not present in the context")
            )
        xmlid = MAP_ACTIONS[analytic_type]
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        records = self.mapped(MAP_FIELDS[analytic_type])
        if len(records) > 1:
            action["domain"] = [("id", "in", records.ids)]
        elif records:
            action["views"] = [
                (self.env.ref(MAP_VIEWS[self._context["analytic_type"]]).id, "form")
            ]
            action["res_id"] = records.id
        return action
