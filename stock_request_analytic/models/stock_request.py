# Copyright 2017-2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockRequest(models.Model):
    _inherit = "stock.request"
    _check_company_auto = True

    analytic_distribution = fields.Json(
        help="Map of analytic account IDs to percentage values.",
    )
    analytic_account_ids = fields.Many2many(
        "account.analytic.account",
        "stock_request_analytic_rel",
        "request_id",
        "analytic_id",
        string="Analytic Accounts",
        help="Materialized analytic accounts derived from analytic_distribution",
    )

    def write(self, vals):
        res = super().write(vals)
        if "analytic_distribution" in vals:
            for rec in self:
                rec._sync_analytic_accounts()
        return res

    def _prepare_stock_moves(self):
        moves_vals = super()._prepare_stock_moves() or []
        distribution = self._get_clean_distribution()
        if isinstance(moves_vals, dict):
            moves_vals = [moves_vals]
        for mv in moves_vals:
            if isinstance(mv, dict):
                mv["analytic_distribution"] = distribution
        return moves_vals

    def _get_clean_distribution(self):
        dist = self.analytic_distribution or {}
        if isinstance(dist, str):
            try:
                dist = json.loads(dist)
            except Exception:
                dist = {}
        if not isinstance(dist, dict):
            dist = {}
        return dist

    def _sync_analytic_accounts(self):
        for rec in self:
            dist = rec.analytic_distribution or {}
            if isinstance(dist, str):
                try:
                    dist = json.loads(dist)
                except Exception:
                    dist = {}
            if not isinstance(dist, dict):
                dist = {}
            analytic_ids = (
                [int(k) for k in dist.keys() if str(k).isdigit()] if dist else []
            )
            if set(rec.analytic_account_ids.ids) != set(analytic_ids):
                rec.analytic_account_ids = [(6, 0, analytic_ids)]

    @api.model_create_multi
    def create(self, vals_list):
        new_vals_list = []
        for vals in vals_list:
            v = dict(vals)
            if "analytic_distribution" not in v and v.get("order_id"):
                order = self.env["stock.request.order"].browse(int(v["order_id"]))
                if order.default_analytic_distribution:
                    dist = order.default_analytic_distribution
                    if isinstance(dist, str):
                        try:
                            dist = json.loads(dist)
                        except Exception:
                            dist = {}
                    v["analytic_distribution"] = dist
            dist = v.get("analytic_distribution") or {}
            if isinstance(dist, str):
                try:
                    dist = json.loads(dist)
                except Exception:
                    dist = {}
            if isinstance(dist, dict) and dist:
                order_id = v.get("order_id")
                company = None
                if order_id:
                    company = (
                        self.env["stock.request.order"].browse(order_id).company_id
                    )
                for aid in dist.keys():
                    try:
                        aid_int = int(aid)
                    except Exception:
                        continue
                    anal = self.env["account.analytic.account"].browse(aid_int)
                    if not anal.company_id:
                        raise UserError(
                            _("Analytic account %s must belong to a company.")
                            % anal.display_name
                        )
                    if company and anal.company_id != company:
                        raise UserError(
                            _("Analytic account %s belongs to another company.")
                            % anal.display_name
                        )
            new_vals_list.append(v)
        records = super().create(new_vals_list)
        for rec in records:
            rec._sync_analytic_accounts()
        return records
