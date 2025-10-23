# Copyright 2025 360 ERP (https://www.360erp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockRoute(models.Model):
    _inherit = "stock.route"

    product_ids = fields.Many2many(
        compute="_compute_product_ids",
        inverse="_inverse_product_ids",
        search="_search_product_ids",
        store=False,
    )
    route_profile_ids = fields.Many2many(
        comodel_name="route.profile",
        string="Route Profiles",
    )

    @api.depends("route_profile_ids.product_ids")
    def _compute_product_ids(self):
        """Reflect the products' default routes as the routes' products"""
        for route in self:
            route.product_ids = self.env["product.template"].search(
                [("route_profile_id.route_ids", "=", route.id)]
            )

    def _inverse_product_ids(self):
        """Reroute the writing of products on routes to the product template model.

        This preserves backwards compatibility for code that insists on setting
        products on routes rather than the other way around. Note that the
        product_ids field is not visible by default on the stock.route form.
        """
        for route in self:
            previous_product_ids = self.env["product.template"].search(
                [("route_profile_id.route_ids", "=", route.id)]
            )
            (previous_product_ids - route.product_ids).write(
                {"route_ids": [fields.Command.unlink(route.id)]}
            )
            (route.product_ids - previous_product_ids).write(
                {"route_ids": [fields.Command.link(route.id)]}
            )

    def _search_product_ids(self, operator, value):
        """Allow to search for products where this route is on the default profile"""
        return [
            (
                "id",
                "in",
                self.env["route.profile"]
                .search(
                    [("product_ids", operator, value)],
                )
                .route_ids.ids,
            ),
        ]
