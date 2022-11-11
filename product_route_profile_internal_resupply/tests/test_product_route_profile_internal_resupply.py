# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestProductRouteProfileInternalResupply(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductRouteProfileInternalResupply, cls).setUpClass()

        cls.company = cls.env.ref("base.main_company")
        cls.env["res.config.settings"].write(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
            }
        )
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh_2 = cls.env["stock.warehouse"].create({"name": "WH2", "code": "WH2"})
        cls.wh.resupply_wh_ids = cls.wh_2

        cls.product = cls.env["product.template"].create(
            {
                "name": "Template 1",
                "company_id": False,
            }
        )

    def test_1_int_supply_route(self):
        self.wh.resupply_wh_ids = self.wh_2
        int_supply_route = self.env["stock.location.route"].search(
            [("internal_supply", "=", True)]
        )
        self.assertTrue(int_supply_route)
        self.product.internal_supply_ids = int_supply_route
        self.assertIn(int_supply_route, self.product.route_ids)
        self.product.internal_supply_ids = False
        self.assertNotIn(int_supply_route, self.product.route_ids)
