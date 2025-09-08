# Copyright 2025 Adriana Saiz (Factor Libre) <adriana.saiz@factorlibre.com>

from odoo import models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _procure_orderpoint_confirm(
        self, use_new_cursor=False, company_id=None, raise_user_error=True
    ):
        """
        Override to set context flags for route-based grouping if any
        orderpoint has a route with 'auto_create_group' enabled.
        """

        route_groups_mapping = {}

        context_with_grouping = {
            "enable_route_grouping": True,
            "route_groups_mapping": route_groups_mapping,
        }

        self = self.with_context(**context_with_grouping)
        return super()._procure_orderpoint_confirm(
            use_new_cursor=use_new_cursor,
            company_id=company_id,
            raise_user_error=raise_user_error,
        )
