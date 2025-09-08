# Copyright 2017-2020 ForgeFlow, S.L.
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2025 Adriana Saiz (Factor Libre) <adriana.saiz@factorlibre.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_rule(self, product_id, location_id, values):
        """
        Override to create/reuse procurement groups based on routes when
        'enable_route_grouping' is set in the context.
        """
        rule = super()._get_rule(product_id, location_id, values)

        if (
            rule
            and rule.auto_create_group
            and values.get("date_planned")
            and self.env.context.get("from_orderpoint")
        ):
            route_id = values.get("route_ids", "no_route")

            route_groups_mapping = dict(
                self.env.context.get("route_groups_mapping", {})
            )
            group = False
            if route_id in route_groups_mapping:
                # Use existing group for this route
                group_id = route_groups_mapping[route_id]
                group = self.env["procurement.group"].browse(group_id)
                if not group.exists():
                    group = False
            if not group:
                # Create new group
                group = rule._get_auto_procurement_group(
                    self.env["product.product"].browse(product_id)
                )
                route_groups_mapping[route_id] = group.id

            values["group_id"] = group

            self.env.context = dict(
                self.env.context, route_groups_mapping=route_groups_mapping
            )

        elif rule and rule.auto_create_group and values.get("date_planned"):
            values["group_id"] = rule._get_auto_procurement_group(product_id)
        return rule
