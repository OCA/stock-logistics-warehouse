# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    route_profile_id = fields.Many2one("route.profile", string="Route Profile")
    force_route_profile_id = fields.Many2one(
        "route.profile",
        string="Priority Route Profile",
        company_dependent=True,
        help="If defined, the "
        "priority route profile will be used and will replace the "
        "route profile, only for this company.",
    )

    route_ids = fields.Many2many(
        compute="_compute_route_ids",
        inverse="_inverse_route_ids",
        search="_search_route_ids",
        store=False,
    )

    def _get_routes(self):
        self.ensure_one()
        if self.force_route_profile_id:
            return self.force_route_profile_id.route_ids
        elif self.route_profile_id:
            return self.route_profile_id.route_ids
        else:
            return self.env["stock.location.route"]

    @api.depends("route_profile_id", "force_route_profile_id")
    @api.depends_context("company")
    def _compute_route_ids(self):
        for rec in self:
            rec.route_ids = rec._get_routes()

    def _search_route_ids(self, operator, value):
        return [
            "|",
            ("force_route_profile_id.route_ids", operator, value),
            "&",
            ("force_route_profile_id", "=", False),
            ("route_profile_id.route_ids", operator, value),
        ]

    def _get_or_create_profile(self, profiles, routes):
        self.ensure_one()
        if not routes:
            return self.env["route.profile"]
        for profile in profiles:
            if routes == profile.route_ids:
                return profile
        vals = self._prepare_profile(routes)
        return self.env["route.profile"].create(vals)

    def _inverse_route_ids(self):
        profiles = self.env["route.profile"].search([])
        for rec in self:
            rec.route_profile_id = rec._get_or_create_profile(profiles, rec.route_ids)

    def _prepare_profile(self, routes):
        return {
            "name": " / ".join(routes.mapped("name")),
            "route_ids": [(6, 0, routes.ids)],
        }
