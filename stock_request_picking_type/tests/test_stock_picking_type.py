# Copyright 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import common


class TestStockRequest(common.TransactionCase):
    @classmethod
    def _create_user(cls, name, group_ids, company_ids):
        return (
            cls.env["res.users"]
            .with_context(**{"no_reset_password": True})
            .create(
                {
                    "name": name,
                    "password": "demo",
                    "login": name,
                    "email": "@".join([name, "test.com"]),
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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # common models
        cls.stock_request = cls.env["stock.request"]
        cls.request_order = cls.env["stock.request.order"]

        # refs
        cls.stock_request_user_group = cls.env.ref(
            "stock_request.group_stock_request_user"
        )
        cls.stock_request_manager_group = cls.env.ref(
            "stock_request.group_stock_request_manager"
        )
        cls.main_company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.categ_unit = cls.env.ref("uom.product_uom_categ_unit")
        cls.default_picking_type = cls.env.ref(
            "stock_request_picking_type.stock_request_order"
        )

        cls.product = cls._create_product("Shoes", "SH", False)
        cls.stock_request_manager = cls._create_user(
            "stock_request_manager",
            [cls.stock_request_manager_group.id],
            [cls.main_company.id],
        )

        cls.ressuply_loc = cls.env["stock.location"].create(
            {
                "name": "Ressuply",
                "location_id": cls.warehouse.view_location_id.id,
                "usage": "internal",
                "company_id": cls.main_company.id,
            }
        )

        cls.route = cls.env["stock.route"].create(
            {
                "name": "Transfer",
                "product_categ_selectable": False,
                "product_selectable": True,
                "company_id": cls.main_company.id,
                "sequence": 10,
            }
        )

        cls.rule = cls.env["stock.rule"].create(
            {
                "name": "Transfer",
                "route_id": cls.route.id,
                "location_src_id": cls.ressuply_loc.id,
                "location_dest_id": cls.warehouse.lot_stock_id.id,
                "action": "pull",
                "picking_type_id": cls.warehouse.int_type_id.id,
                "procure_method": "make_to_stock",
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.main_company.id,
            }
        )

        cls.env["ir.config_parameter"].sudo().set_param(
            "stock.no_auto_scheduler", "True"
        )


class TestStockPickingType(TestStockRequest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_compute_sr_count(self):
        expected_date = fields.Datetime.now()
        late_expected_date = fields.Datetime.now() - relativedelta(days=1)
        order_vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": expected_date,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "company_id": self.main_company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.warehouse.lot_stock_id.id,
                        "expected_date": expected_date,
                    },
                )
            ],
        }

        order = self.request_order.with_user(self.stock_request_manager).create(
            order_vals
        )
        self.product.route_ids = [(6, 0, self.route.ids)]
        self.assertEqual(order.picking_type_id.count_sr_todo, 0)
        self.assertEqual(order.picking_type_id.count_sr_open, 0)
        self.assertEqual(order.picking_type_id.count_sr_late, 0)

        order.with_user(self.stock_request_manager).action_confirm()
        order.picking_type_id.sudo()._compute_sr_count()

        # check count_sr_open
        self.assertEqual(order.picking_type_id.count_sr_todo, 0)
        self.assertEqual(order.picking_type_id.count_sr_open, 1)
        self.assertEqual(order.picking_type_id.count_sr_late, 0)

        order.expected_date = late_expected_date
        order.picking_type_id.sudo()._compute_sr_count()
        self.assertEqual(order.picking_type_id.count_sr_todo, 0)
        self.assertEqual(order.picking_type_id.count_sr_open, 1)
        self.assertEqual(order.picking_type_id.count_sr_late, 1)
