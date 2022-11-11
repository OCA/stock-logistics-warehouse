# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RouteProfile(models.Model):
    _inherit = "route.profile"

    route_ids = fields.Many2many(
        "stock.location.route",
        string="Routes",
        domain=[("product_selectable", "=", True), ("internal_supply", "=", False)],
    )
