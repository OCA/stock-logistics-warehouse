# Copyright 2020-2021 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2022-2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def is_sublocation_of(self, others, func=any):
        """Return True if self is a sublocation of others (or equal)

        By default, it return True if any other is a parent or equal.
        ``all`` can be passed to ``func`` to require all the other locations
        to be parent or equal to be True.
        """
        self.ensure_one()
        # Efficient way to verify that the current location is
        # below one of the other location without using SQL.
        return func(self.parent_path.startswith(other.parent_path) for other in others)

    def _get_source_location_from_route(self, route, procure_method):
        self.ensure_one()
        route.ensure_one()
        values = {
            "route_ids": route,
        }
        current_location = self
        while current_location:
            rule = self.env["procurement.group"]._get_rule(
                self.env["product.product"], current_location, values
            )
            if not rule:
                return self.browse()
            if rule.procure_method == procure_method:
                return rule.location_src_id
            current_location = rule.location_src_id
