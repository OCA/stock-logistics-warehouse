# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    default_analytic_distribution = fields.Json(
        help="Default analytic distribution applied to new request lines.",
    )
    analytic_count = fields.Integer(
        compute="_compute_analytic_count",
        store=False,
    )

    @api.depends("stock_request_ids.analytic_distribution")
    def _compute_analytic_count(self):
        for order in self:
            keys = set()
            for req in order.stock_request_ids:
                dist = req.analytic_distribution or {}
                if isinstance(dist, str):
                    try:
                        dist = json.loads(dist)
                    except Exception:
                        dist = {}
                if isinstance(dist, dict):
                    keys.update(dist.keys())
            order.analytic_count = len(keys)

    def action_view_analytic(self):
        self.ensure_one()
        analytic_ids = set()
        for req in self.stock_request_ids:
            dist = req.analytic_distribution or {}
            if isinstance(dist, str):
                try:
                    dist = json.loads(dist)
                except Exception:
                    dist = {}
            if isinstance(dist, dict):
                analytic_ids.update(dist.keys())
        analytic_ids = list(map(int, analytic_ids)) if analytic_ids else []
        action = self.env["ir.actions.actions"]._for_xml_id(
            "analytic.action_account_analytic_account_form"
        )
        action["domain"] = [("id", "in", analytic_ids)]
        if len(analytic_ids) == 1:
            action["res_id"] = analytic_ids[0]
            action["views"] = [(False, "form")]
        return action

    def _validate_company_rules(self, order):
        for line in order.stock_request_ids:
            dist = line.analytic_distribution or {}
            if isinstance(dist, str):
                try:
                    dist = json.loads(dist)
                except Exception:
                    dist = {}
            if not isinstance(dist, dict):
                continue
            for aid in dist.keys():
                try:
                    aid_int = int(aid)
                except Exception:
                    continue
                analytic = self.env["account.analytic.account"].browse(aid_int)
                if not analytic.company_id:
                    raise UserError(
                        _("Analytic account %s must belong to a company.")
                        % analytic.display_name
                    )
                if analytic.company_id != order.company_id:
                    raise UserError(
                        _("Analytic account %s belongs to another company.")
                        % analytic.display_name
                    )

    def _apply_default_analytic_distribution(self, order):
        default_dist = order.default_analytic_distribution or {}
        if isinstance(default_dist, str):
            try:
                default_dist = json.loads(default_dist)
            except Exception:
                default_dist = {}
        if not isinstance(default_dist, dict) or not default_dist:
            return
        for line in order.stock_request_ids:
            if not line.analytic_distribution:
                line.analytic_distribution = default_dist
                if hasattr(line, "_sync_analytic_accounts"):
                    line._sync_analytic_accounts()

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            self._validate_company_rules(order)
            self._apply_default_analytic_distribution(order)
        return orders
