# Copyright 2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    route_ids = fields.Many2many(
        "stock.location.route", string="Allowed routes", compute="_compute_route_ids"
    )
    route_id = fields.Many2one(
        "stock.location.route",
        string="Route",
        domain="[('id', 'in', route_ids)]",
        ondelete="restrict",
    )

    @api.depends("product_id", "warehouse_id", "warehouse_id.route_ids", "location_id")
    def _compute_route_ids(self):
        route_obj = self.env["stock.location.route"]
        for record in self:
            wh_routes = record.warehouse_id.route_ids
            routes = route_obj.browse()
            if record.product_id:
                routes += record.product_id.mapped(
                    "route_ids"
                ) | record.product_id.mapped("categ_id").mapped("total_route_ids")
            if record.warehouse_id:
                routes |= wh_routes
            parents = record.get_parents()
            record.route_ids = self._get_location_routes_of_parents(routes, parents)

    def _get_location_routes_of_parents(self, routes, parents):
        return routes.filtered(
            lambda route: any(
                p.location_id in parents
                for p in route.rule_ids.filtered(
                    lambda rule: rule.action in ("pull", "pull_push")
                ).mapped("location_src_id")
            )
        )

    def get_parents(self):
        return self.env["stock.location"].search(
            [("id", "parent_of", self.location_id.id)]
        )

    def _prepare_procurement_values(self, date=False, group=False):
        res = super()._prepare_procurement_values(date=date, group=group)
        res["route_ids"] = self.route_id
        return res
