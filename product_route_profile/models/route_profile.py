# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RouteProfile(models.Model):
    _name = "route.profile"
    _description = "Route Profile"

    name = fields.Char()
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company.id,
        required=False,
        string="Company",
    )
    route_ids = fields.Many2many(
        "stock.location.route",
        string="Routes",
        domain=[("product_selectable", "=", True)],
    )
