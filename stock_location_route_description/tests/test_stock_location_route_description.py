# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockLocationRouteDescription(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestStockLocationRouteDescription, self).setUp(*args, **kwargs)
        self.model_stock_location_route = self.env["stock.location.route"]

    def test_display_name_stock_location_route(self):
        """
            Test to display the name of the route with and without a context.
        """
        route = self.model_stock_location_route.create(
            {"name": "Test Route", "description": "Test Description"}
        )
        self.assertEqual(route.display_name, route.name)
        name_description = route.name + ": " + route.description
        route.with_context(show_description=True)._compute_display_name()
        self.assertEqual(route.display_name, name_description)
