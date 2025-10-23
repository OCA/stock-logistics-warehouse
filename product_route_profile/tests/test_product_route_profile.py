# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestProductRouteProfile(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company_bis = cls.env["res.company"].create(
            {
                "name": "company 2",
                "parent_id": cls.env.ref("base.main_company").id,
            }
        )

        cls.route_1 = cls.env.ref("stock.route_warehouse0_mto")
        cls.route_1.active = True
        cls.route_2 = cls.route_1.copy({"name": "route 2"})

        cls.route_profile_1 = cls.env["route.profile"].create(
            {
                "name": "profile 1",
                "route_ids": [Command.set(cls.route_1.ids)],
            }
        )
        cls.route_profile_2 = cls.env["route.profile"].create(
            {
                "name": "profile 2",
                "route_ids": [Command.set(cls.route_2.ids)],
            }
        )

        cls.product = cls.env["product.template"].create(
            {
                "name": "Template 1",
                "company_id": False,
            }
        )

    def test_1_route_profile(self):
        self.product.route_profile_id = self.route_profile_1.id
        self.assertEqual(self.product.route_ids, self.route_profile_1.route_ids)
        # In other company, no change
        self.assertEqual(
            self.product.with_company(self.company_bis).route_ids,
            self.route_profile_1.route_ids,
        )

    def test_2_force_route_profile(self):
        self.product.route_profile_id = self.route_profile_1.id
        self.product.with_company(
            self.env.company
        ).force_route_profile_id = self.route_profile_2.id
        self.assertEqual(self.product.route_profile_id, self.route_profile_1)
        self.assertEqual(
            self.product.with_company(self.env.company).route_ids,
            self.route_profile_2.route_ids,
        )
        # In other company, no change
        self.assertEqual(
            self.product.with_company(self.company_bis).route_ids,
            self.route_profile_1.route_ids,
        )
        # Return to route_profile_id if no force_route_profile_id
        self.product.with_company(self.env.company).force_route_profile_id = False
        self.assertEqual(
            self.product.with_company(self.env.company).route_ids,
            self.route_profile_1.route_ids,
        )

    def test_3_product_creation_with_route_profile(self):
        product = self.env["product.template"].create(
            {
                "name": "Template 2",
                "company_id": False,
                "route_profile_id": self.route_profile_1.id,
            }
        )

        self.assertEqual(product.route_profile_id.id, self.route_profile_1.id)

    def test_set_product_route_ids(self):
        """Test backwards compatibility setting routes on products"""
        product = self.env["product.template"].create(
            {
                "name": __name__,
                "company_id": False,
            }
        )
        product.route_ids = self.route_1 + self.route_2
        self.assertEqual(
            product.route_ids,
            self.route_1 + self.route_2,
        )
        self.assertEqual(
            product.route_profile_id.route_ids,
            self.route_1 + self.route_2,
        )
        self.assertIn(
            product,
            self.env["product.template"].search(
                [("route_ids", "=", self.route_1.id)],
            ),
        )
        self.assertIn(
            product,
            self.env["product.template"].search(
                [("route_ids", "=", self.route_2.id)],
            ),
        )

        # Product is reflected on the routes
        self.assertIn(product, self.route_1.product_ids)
        self.assertIn(product, self.route_2.product_ids)
        self.assertIn(
            self.route_1,
            self.env["stock.route"].search([("product_ids", "=", product.id)]),
        )
        self.assertIn(
            self.route_2,
            self.env["stock.route"].search([("product_ids", "=", product.id)]),
        )

        # Now modify the product on one of the routes
        self.route_2.product_ids -= product

        self.assertEqual(
            product.route_ids,
            self.route_1,
        )
        self.assertEqual(
            product.route_profile_id.route_ids,
            self.route_1,
        )
        self.assertIn(
            product,
            self.env["product.template"].search(
                [("route_ids", "=", self.route_1.id)],
            ),
        )
        self.assertNotIn(
            product,
            self.env["product.template"].search(
                [("route_ids", "=", self.route_2.id)],
            ),
        )

        self.assertIn(product, self.route_1.product_ids)
        self.assertNotIn(product, self.route_2.product_ids)
        self.assertIn(
            self.route_1,
            self.env["stock.route"].search([("product_ids", "=", product.id)]),
        )
        self.assertNotIn(
            self.route_2,
            self.env["stock.route"].search([("product_ids", "=", product.id)]),
        )
