# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestScrapLocationDefault(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        parent_location = cls.env.ref(
            "stock.stock_location_locations_virtual", raise_if_not_found=False
        )
        cls.product = cls.env["product.product"].create({"name": "Test"})
        cls.company = cls.env.ref("base.main_company")
        cls.company_2 = cls.env["res.company"].create(
            {
                "name": "Company 2 (test scrap)",
            }
        )
        # As creating new company creates also a scrap location
        cls.scrap_location = cls.env["stock.location"].search(
            [("company_id", "=", cls.company_2.id), ("scrap_location", "=", True)],
            limit=1,
        )
        cls.scrap_location_2 = cls.env["stock.location"].create(
            {
                "name": "Test Scrap 2",
                "location_id": parent_location.id,
                "company_id": cls.company_2.id,
                "scrap_location": True,
            }
        )
        cls.scrap_location_3 = cls.env["stock.location"].create(
            {
                "name": "Test Scrap 3",
                "location_id": parent_location.id,
                "company_id": cls.company_2.id,
                "scrap_location": True,
            }
        )
        cls.scrap_location_4 = cls.env["stock.location"].create(
            {
                "name": "Test Scrap 4",
                "location_id": parent_location.id,
                "company_id": cls.company.id,
                "scrap_location": True,
            }
        )
        # Set advanced locations group
        cls.env.user.groups_id += cls.env.ref("stock.group_stock_multi_locations")

    def test_scrap_location_default(self):
        # Set default scrap location on company 2
        # Should be that one that is selected
        # Set the scrap location 4 on main company
        # Check if both different default scrap location are used
        self.company_2.scrap_default_location_id = self.scrap_location_3
        scrap_form = Form(self.env["stock.scrap"].with_company(self.company_2))

        scrap_form.product_id = self.product
        self.assertEqual(self.scrap_location_3, scrap_form.scrap_location_id)

        # Set default on main company
        self.company.scrap_default_location_id = self.scrap_location_4

        # Check behaviour on main company
        scrap_form = Form(self.env["stock.scrap"].with_company(self.company))
        scrap_form.product_id = self.product
        self.assertEqual(self.scrap_location_4, scrap_form.scrap_location_id)

        # Check again behaviour on company 2
        scrap_form = Form(self.env["stock.scrap"].with_company(self.company_2))
        scrap_form.product_id = self.product
        self.assertEqual(self.scrap_location_3, scrap_form.scrap_location_id)

    def test_scrap_location_no_default(self):
        # Set no default scrap location
        # Should be the one created with company
        scrap_form = Form(self.env["stock.scrap"].with_company(self.company_2))
        scrap_form.product_id = self.product
        self.assertTrue(self.scrap_location)
        self.assertEqual(self.scrap_location, scrap_form.scrap_location_id)
