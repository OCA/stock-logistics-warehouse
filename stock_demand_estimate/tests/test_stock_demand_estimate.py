# Copyright 2017-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import date, timedelta as td

from odoo.tests.common import SavepointCase


class TestStockDemandEstimate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.res_users_model = cls.env["res.users"]
        cls.product_model = cls.env["product.product"]
        cls.stock_location_model = cls.env["stock.location"]
        cls.estimate_model = cls.env["stock.demand.estimate"]

        cls.g_stock_manager = cls.env.ref("stock.group_stock_manager")
        cls.g_stock_user = cls.env.ref("stock.group_stock_user")
        cls.company = cls.env.ref("base.main_company")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")

        # Create users:
        cls.manager = cls._create_user("user_1", [cls.g_stock_manager], cls.company).id
        cls.user = cls._create_user("user_2", [cls.g_stock_user], cls.company).id

        # Create a product:
        cls.product_1 = cls.product_model.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "default_code": "PROD1",
                "uom_id": cls.uom_unit.id,
            }
        )
        # Create a location:
        cls.location = cls.stock_location_model.create(
            {"name": "Place", "usage": "production"}
        )

    @classmethod
    def _create_user(cls, login, groups, company):
        group_ids = [group.id for group in groups]
        user = cls.res_users_model.create(
            {
                "name": login,
                "login": login,
                "password": "demo",
                "email": "example@yourcompany.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "groups_id": [(6, 0, group_ids)],
            }
        )
        return user

    def test_01_create_estimate(self):
        """Crete an estimate entering manually the date from and date to."""
        date_from = date.today() + td(days=10)
        date_to = date.today() + td(days=19)
        estimate = self.estimate_model.create(
            {
                "product_id": self.product_1.id,
                "location_id": self.location.id,
                "manual_date_from": date_from,
                "manual_date_to": date_to,
                "product_uom_qty": 500.0,
            }
        )
        self.assertEqual(estimate.date_from, date_from)
        self.assertEqual(estimate.date_to, date_to)
        self.assertEqual(estimate.duration, 10)
        self.assertEqual(estimate.product_qty, 500.0)
        self.assertEqual(estimate.daily_qty, 500.0 / 10.0)

    def test_02_create_estimate_by_duration_and_different_uom(self):
        """Create an estimate entering manually the date from, duration and
        using a different UoM than product's."""
        date_from = date.today() + td(days=10)
        estimate = self.estimate_model.create(
            {
                "product_id": self.product_1.id,
                "location_id": self.location.id,
                "manual_date_from": date_from,
                "manual_duration": 15,
                "product_uom_qty": 100.0,
                "product_uom": self.uom_dozen.id,
            }
        )
        self.assertEqual(estimate.date_from, date_from)
        expected_date_to = estimate.date_from + td(days=15 - 1)
        self.assertEqual(estimate.date_to, expected_date_to)
        self.assertEqual(estimate.duration, 15)
        expected_qty = 100 * 12.0  # 100 dozens -> units
        self.assertEqual(estimate.product_qty, expected_qty)
        self.assertEqual(estimate.daily_qty, expected_qty / 15)

    def test_03_get_qty_by_range(self):
        date_from = date.today() + td(days=10)
        date_to = date.today() + td(days=19)
        estimate = self.estimate_model.create(
            {
                "product_id": self.product_1.id,
                "location_id": self.location.id,
                "manual_date_from": date_from,
                "manual_date_to": date_to,
                "product_uom_qty": 100.0,
            }
        )
        self.assertEqual(estimate.duration, 10.0)
        self.assertEqual(estimate.daily_qty, 10.0)
        res = estimate.get_quantity_by_date_range(
            date_from + td(days=3), date_from + td(days=17)
        )
        self.assertEqual(res, 70)
        res = estimate.get_quantity_by_date_range(
            date_from + td(days=3), date_from + td(days=7)
        )
        self.assertEqual(res, 50)
        # get full period
        res = estimate.get_quantity_by_date_range(date.today(), date_from + td(days=17))
        self.assertEqual(res, 100)
        # Get exact period:
        res = estimate.get_quantity_by_date_range(estimate.date_from, estimate.date_to)
        self.assertEqual(res, 100)
        # Ask for interval out fo the estimate's:
        res = estimate.get_quantity_by_date_range(
            date.today(), date.today() + td(days=8)
        )
        self.assertEqual(res, 0)

    def test_04_name_get(self):
        date_from = date.today() + td(days=10)
        estimate = self.estimate_model.create(
            {
                "product_id": self.product_1.id,
                "location_id": self.location.id,
                "manual_date_from": date_from,
                "manual_duration": False,  # to test else case in _compute_dates.
                "product_uom_qty": 500.0,
            }
        )
        res = estimate.name_get()
        self.assertEqual(len(res), 1)
        rec_id, name_get = res[0]
        self.assertEqual(estimate.id, rec_id)
        self.assertIn(self.product_1.name, name_get)

    def test_05_onchange_methods(self):
        date_from = date.today() + td(days=10)
        date_to = date.today() + td(days=19)
        estimate = self.estimate_model.new(
            {
                "product_id": self.product_1.id,
                "location_id": self.location.id,
                "manual_date_from": date_from,
                "manual_date_to": date_to,
                "product_uom_qty": 500.0,
            }
        )
        estimate._onchange_manual_date_to()
        self.assertEqual(estimate.manual_duration, 10)
        # Change duration manually:
        estimate.manual_duration = 5
        estimate._onchange_manual_duration()
        self.assertEqual(estimate.manual_date_to, date_from + td(days=4))
