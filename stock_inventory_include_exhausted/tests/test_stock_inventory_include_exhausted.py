# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class StockInventoryIncludeExhaustedTest(TransactionCase):
    def setUp(self):
        super().setUp()

        self.inventory_model = self.env["stock.inventory"]
        self.location_model = self.env["stock.location"]
        self.res_users_model = self.env["res.users"]

        self.company = self.env.ref("base.main_company")
        self.partner = self.ref("base.res_partner_4")

        # We need this to know how many product with no stock we have on our
        # database
        self.quantity_out_of_stock = len(
            self.env["product.product"].search(
                [("qty_available", "=", 0), ("type", "=", "product")]
            )
        )

        self.user = self.res_users_model.create(
            {
                "name": "Test Account User",
                "login": "user_1",
                "email": "example@yourcompany.com",
                "company_id": self.company.id,
                "company_ids": [(4, self.company.id)],
            }
        )

        self.product1 = self.env["product.product"].create(
            {
                "name": "Product for parent location",
                "type": "product",
                "default_code": "PROD1",
            }
        )
        self.product2 = self.env["product.product"].create(
            {
                "name": "Product for child location",
                "type": "product",
                "default_code": "PROD2",
            }
        )

        self.location = self.location_model.create(
            {"name": "Inventory tests 1", "usage": "internal"}
        )

    def _create_inventory_all_products(self, name, location, include_exhausted):
        inventory = self.inventory_model.create(
            {
                "name": name,
                "location_ids": [(4, location.id)],
                "include_exhausted": include_exhausted,
            }
        )
        return inventory

    def test_not_including_exhausted(self):
        """Check if products with no stock are not included into the inventory
        if the including exhausted option is disabled."""
        inventory_not_inc = self._create_inventory_all_products(
            "not_included", self.location, False
        )
        inventory_not_inc.action_start()
        inventory_not_inc.action_validate()
        lines = inventory_not_inc.line_ids
        self.assertEqual(len(lines), 0, "Not all expected products are included")

    def test_including_exhausted(self):
        """Check if products with no stock are included into the inventory
        if the including exhausted option is enabled."""
        inventory_inc = self._create_inventory_all_products(
            # The products with no stock don't have a location,
            # that's why search the non-stocked in all locations
            "included",
            self.location,
            True,
        )

        inventory_inc.action_start()
        inventory_inc.action_validate()
        lines = inventory_inc.line_ids
        self.assertEqual(
            len(lines),
            self.quantity_out_of_stock + 2,
            "The products with no stock are not included",
        )
