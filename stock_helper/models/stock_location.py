# Copyright 2020-2021 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2022 Michael Tietz (MT Software) <mtietz@mt-software.de>
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

    def get_closest_warehouse(self):
        """Returns closest warehouse for current location.

        By default the get_warehouse (which is located in the odoo core module stock)
        returns the warehouse via searching the view_location_id with parent_of.
        If we have multiple warehouses
        where a view_location_id is a parent of an other view_location_id
        Then it depends on the sorting of the warehouses which this method returns

        With this methods we will really get the closest warehouse of a location
        """
        self.ensure_one()
        location_ids = [int(x) for x in self.parent_path.split("/") if x]
        warehouses = (
            self.env["stock.warehouse"]
            .search([("view_location_id", "in", location_ids)])
            .sorted(lambda w: w.view_location_id.parent_path, reverse=True)
        )
        for warehouse in warehouses:
            if self.parent_path.startswith(warehouse.view_location_id.parent_path):
                return warehouse
        return warehouses.browse()
