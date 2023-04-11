# Copyright 2020-2021 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from collections import OrderedDict

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

    def _compute_warehouse_id(self):
        """Computes closest warehouse for locations.

        By default the _compute_warehouse_id (which is located in the odoo core module stock)
        returns the warehouse via searching the view_location_id with parent_of.
        If we have multiple warehouses
        where a view_location_id is a parent of an other view_location_id
        Then it depends on the sorting of the warehouses which warehouse gets set

        With this overwrite we will really set the closest warehouse of a location
        """
        warehouses = self.env["stock.warehouse"].search(
            [("view_location_id", "parent_of", self.ids)]
        )
        view_by_wh = OrderedDict(
            (wh.view_location_id.id, wh.id)
            for wh in warehouses.sorted(
                lambda w: w.view_location_id.parent_path, reverse=True
            )
        )
        self.warehouse_id = False
        for loc in self:
            if not loc.parent_path:
                continue
            path = {int(loc_id) for loc_id in loc.parent_path.split("/")[:-1]}
            for view_location_id in view_by_wh:
                if view_location_id in path:
                    loc.warehouse_id = view_by_wh[view_location_id]
                    break
