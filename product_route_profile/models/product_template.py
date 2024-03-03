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

    @api.depends("route_profile_id", "force_route_profile_id")
    @api.depends_context("company")
    def _compute_route_ids(self):
        for rec in self.sudo():
            if rec.force_route_profile_id:
                rec.route_ids = [(6, 0, rec.force_route_profile_id.route_ids.ids)]
            elif rec.route_profile_id:
                rec.route_ids = [(6, 0, rec.route_profile_id.route_ids.ids)]
            else:
                rec.route_ids = False

    def _search_route_ids(self, operator, value):
        return [
            "|",
            ("force_route_profile_id.route_ids", operator, value),
            "&",
            ("force_route_profile_id", "=", False),
            ("route_profile_id.route_ids", operator, value),
        ]

    def _inverse_route_ids(self):
        if self._context.get("skip_inverse_route_ids"):
            return
        profiles = self.env["route.profile"].search([])
        for rec in self:
            for profile in profiles:
                if rec.route_ids == profile.route_ids:
                    rec.route_profile_id = profile
                    break
            else:
                vals = rec._prepare_profile()
                rec.route_profile_id = self.env["route.profile"].create(vals)

    def _prepare_profile(self):
        return {
            "name": " / ".join(self.route_ids.mapped("name")),
            "route_ids": [(6, 0, self.route_ids.ids)],
        }

    @api.model
    def create(self, vals):
        route_profile_id = vals.get("route_profile_id", False)
        if route_profile_id:
            route_profile = self.env["route.profile"].browse(route_profile_id)
            vals["route_ids"] = [(6, 0, route_profile.route_ids.ids)]
            self = self.with_context(skip_inverse_route_ids=True)
        return super(ProductTemplate, self).create(vals)
