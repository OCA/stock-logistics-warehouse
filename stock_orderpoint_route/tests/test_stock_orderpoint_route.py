# Copyright 2017 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common


class TestStockOrderpointRoute(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # common models
        cls.orderpoint_model = cls.env["stock.warehouse.orderpoint"]
        cls.procurement_group_model = cls.env["procurement.group"]
        # refs
        cls.stock_manager_group = cls.env.ref("stock.group_stock_manager")
        cls.stock_multi_locations_group_group = cls.env.ref(
            "stock.group_stock_multi_locations"
        )
        cls.main_company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.categ_unit = cls.env.ref("uom.product_uom_categ_unit")
        cls.virtual_loc = cls.env.ref("stock.stock_location_customers")

        # common data
        cls.stock_manager = cls._create_user(
            "stock_manager",
            [cls.stock_manager_group.id, cls.stock_multi_locations_group_group.id],
            [cls.main_company.id],
        )
        cls.product = cls._create_product("SH", "Shoes", False)

        cls.ressuply_loc = cls.env["stock.location"].create(
            {"name": "Ressuply", "location_id": cls.warehouse.view_location_id.id}
        )

        cls.ressuply_loc2 = cls.env["stock.location"].create(
            {"name": "Ressuply2", "location_id": cls.warehouse.view_location_id.id}
        )

        cls.route = cls.env["stock.location.route"].create(
            {
                "name": "Transfer",
                "product_categ_selectable": False,
                "product_selectable": True,
                "company_id": cls.main_company.id,
                "sequence": 10,
            }
        )
        cls.route2 = cls.env["stock.location.route"].create(
            {
                "name": "Transfer",
                "product_categ_selectable": False,
                "product_selectable": True,
                "company_id": cls.main_company.id,
                "sequence": 10,
            }
        )

        cls.uom_dozen = cls.env["uom.uom"].create(
            {
                "name": "Test-DozenA",
                "category_id": cls.categ_unit.id,
                "factor_inv": 12,
                "uom_type": "bigger",
                "rounding": 0.001,
            }
        )

        cls.env["stock.rule"].create(
            {
                "name": "Transfer",
                "route_id": cls.route.id,
                "location_src_id": cls.ressuply_loc.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "action": "pull",
                "picking_type_id": cls.warehouse.int_type_id.id,
                "procure_method": "make_to_stock",
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.main_company.id,
            }
        )

        cls.env["stock.rule"].create(
            {
                "name": "Transfer 2",
                "route_id": cls.route2.id,
                "location_src_id": cls.ressuply_loc2.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "action": "pull",
                "picking_type_id": cls.warehouse.int_type_id.id,
                "procure_method": "make_to_stock",
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.main_company.id,
            }
        )

    @classmethod
    def _create_user(cls, name, group_ids, company_ids):
        return (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": name,
                    "password": "demo",
                    "login": name,
                    "email": "@".join([name, "@test.com"]),
                    "groups_id": [(6, 0, group_ids)],
                    "company_ids": [(6, 0, company_ids)],
                }
            )
        )

    @classmethod
    def _create_product(cls, default_code, name, company_id, **vals):
        return cls.env["product.product"].create(
            dict(
                name=name,
                default_code=default_code,
                uom_id=cls.env.ref("uom.product_uom_unit").id,
                company_id=company_id,
                type="product",
                **vals
            )
        )

    def test_orderpoint_route_01(self):
        self.product.route_ids = [(6, 0, [self.route.id, self.route2.id])]
        vals = {
            "product_id": self.product.id,
            "product_min_qty": 10.0,
            "product_max_qty": 100.0,
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "qty_to_order": 11.0,
        }

        orderpoint = self.orderpoint_model.with_user(self.stock_manager).create(vals)
        self.assertIn(self.route, orderpoint.route_ids)
        self.assertIn(self.route2, orderpoint.route_ids)
        orderpoint.route_id = self.route.id
        self.procurement_group_model.run_scheduler()
        move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.ressuply_loc.id),
            ],
            limit=1,
        )
        self.assertEqual(len(move), 1)

    def test_orderpoint_route_02(self):
        self.product.route_ids = [(6, 0, [self.route.id, self.route2.id])]
        vals = {
            "product_id": self.product.id,
            "product_min_qty": 10.0,
            "product_max_qty": 100.0,
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "qty_to_order": 11.0,
        }

        orderpoint = self.orderpoint_model.with_user(self.stock_manager).create(vals)
        self.assertIn(self.route, orderpoint.route_ids)
        self.assertIn(self.route2, orderpoint.route_ids)
        orderpoint.route_id = self.route2.id
        self.procurement_group_model.run_scheduler()
        move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.ressuply_loc2.id),
            ],
            limit=1,
        )
        self.assertEqual(len(move), 1)
