# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


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
                "route_ids": [(6, 0, [cls.route_1.id])],
            }
        )
        cls.route_profile_2 = cls.env["route.profile"].create(
            {
                "name": "profile 2",
                "route_ids": [(6, 0, [cls.route_2.id])],
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
