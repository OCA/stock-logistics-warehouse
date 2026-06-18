# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RouteProfile(models.Model):
    _name = "route.profile"
    _description = "Route Profile"

    def _domain_route_ids(self):
        return [("product_selectable", "=", True)]

    name = fields.Char()
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company.id,
        required=False,
    )
    route_ids = fields.Many2many(
        comodel_name="stock.route",
        string="Routes",
        domain=lambda self: self._domain_route_ids(),
    )
    product_ids = fields.One2many(
        comodel_name="product.template",
        inverse_name="route_profile_id",
        string="Products (default)",
    )
