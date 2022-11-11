# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    internal_supply_ids = fields.Many2many(
        comodel_name="stock.location.route",
        string="internal Supplies",
        domain=[
            ("internal_supply", "=", True),
        ],
    )

    @api.depends("internal_supply_ids")
    def _compute_route_ids(self):
        super()._compute_route_ids()

    def _get_routes(self):
        return super()._get_routes() | self.internal_supply_ids

    def _get_or_create_profile(self, profiles, routes):
        routes -= self.internal_supply_ids
        return super()._get_or_create_profile(profiles, routes)

    def _search_route_ids(self, operator, value):
        res = super()._search_route_ids(operator, value)
        res.insert(1, '"|", ("internal_supply_ids", operator, value),')
        return res
