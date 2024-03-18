# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockInventoryExcludeSublocation(TransactionCase):
    def setUp(self):
        super(TestStockInventoryExcludeSublocation, self).setUp()
        self.inventory_model = self.env["stock.inventory"]
        self.location_model = self.env["stock.location"]
        self.res_users_model = self.env["res.users"]

        self.company = self.env.ref("base.main_company")
        self.partner = self.ref("base.res_partner_4")
        self.grp_stock_manager = self.env.ref("stock.group_stock_manager")

        self.user = self.res_users_model.create(
            {
                "name": "Test Account User",
                "login": "user_1",
                "email": "example@yourcompany.com",
                "company_id": self.company.id,
                "company_ids": [(4, self.company.id)],
                "groups_id": [(6, 0, [self.grp_stock_manager.id])],
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
            {"name": "Inventory tests", "usage": "internal"}
        )
        self.sublocation = self.location_model.create(
            {
                "name": "Inventory sublocation test",
                "usage": "internal",
                "location_id": self.location.id,
            }
        )

        # Add a product in each location
        starting_inv = self.inventory_model.create(
            {
                "name": "Starting inventory",
                "stock_quant_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "inventory_quantity": 2.0,
                            "location_id": self.location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product2.id,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "inventory_quantity": 4.0,
                            "location_id": self.sublocation.id,
                        },
                    ),
                ],
            }
        )
        starting_inv.action_state_to_in_progress()
        starting_inv.action_state_to_done()

    def _create_inventory_all_products(self, name, location, exclude_sublocation):
        inventory = self.inventory_model.create(
            {
                "name": name,
                "location_ids": [(4, location.id)],
                "exclude_sublocation": exclude_sublocation,
            }
        )
        return inventory

    def test_not_excluding_sublocations(self):
        """Check if products in sublocations are included into the inventory
        if the excluding sublocations option is disabled."""
        inventory_location = self._create_inventory_all_products(
            "location inventory", self.location, False
        )
        inventory_location.action_state_to_in_progress()
        inventory_location.action_state_to_done()
        lines = inventory_location.stock_quant_ids
        self.assertEqual(len(lines), 2, "Not all expected products are " "included")

    def test_excluding_sublocations(self):
        """Check if products in sublocations are not included if the exclude
        sublocations is enabled."""
        inventory_location = self._create_inventory_all_products(
            "location inventory", self.location, True
        )
        inventory_sublocation = self._create_inventory_all_products(
            "sublocation inventory", self.sublocation, True
        )
        inventory_location.action_state_to_in_progress()
        inventory_location.action_state_to_done()
        inventory_sublocation.action_state_to_in_progress()
        inventory_sublocation.action_state_to_done()
        lines_location = inventory_location.stock_quant_ids
        lines_sublocation = inventory_sublocation.stock_quant_ids
        self.assertEqual(
            len(lines_location), 1, "The products in the sublocations are not excluded"
        )
        self.assertEqual(
            len(lines_sublocation),
            1,
            "The products in the sublocations are not excluded",
        )
