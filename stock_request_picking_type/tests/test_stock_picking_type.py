# Copyright 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import common


class TestStockRequest(common.TransactionCase):
    def setUp(self):
        super(TestStockRequest, self).setUp()

        # common models
        self.stock_request = self.env["stock.request"]
        self.request_order = self.env["stock.request.order"]

        # refs
        self.stock_request_user_group = self.env.ref(
            "stock_request.group_stock_request_user"
        )
        self.stock_request_manager_group = self.env.ref(
            "stock_request.group_stock_request_manager"
        )
        self.main_company = self.env.ref("base.main_company")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.categ_unit = self.env.ref("uom.product_uom_categ_unit")
        self.default_picking_type = self.env.ref(
            "stock_request_picking_type.stock_request_order"
        )

        self.product = self._create_product("SH", "Shoes", False)
        self.stock_request_manager = self._create_user(
            "stock_request_manager",
            [self.stock_request_manager_group.id],
            [self.main_company.id],
        )

        self.ressuply_loc = self.env["stock.location"].create(
            {
                "name": "Ressuply",
                "location_id": self.warehouse.view_location_id.id,
                "usage": "internal",
                "company_id": self.main_company.id,
            }
        )

        self.route = self.env["stock.location.route"].create(
            {
                "name": "Transfer",
                "product_categ_selectable": False,
                "product_selectable": True,
                "company_id": self.main_company.id,
                "sequence": 10,
            }
        )

        self.rule = self.env["stock.rule"].create(
            {
                "name": "Transfer",
                "route_id": self.route.id,
                "location_src_id": self.ressuply_loc.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "action": "pull",
                "picking_type_id": self.warehouse.int_type_id.id,
                "procure_method": "make_to_stock",
                "warehouse_id": self.warehouse.id,
                "company_id": self.main_company.id,
            }
        )

        self.env["ir.config_parameter"].sudo().set_param(
            "stock.no_auto_scheduler", "True"
        )

    def _create_user(self, name, group_ids, company_ids):
        return (
            self.env["res.users"]
            .with_context({"no_reset_password": True})
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

    def _create_product(self, default_code, name, company_id, **vals):
        return self.env["product.product"].create(
            dict(
                name=name,
                default_code=default_code,
                uom_id=self.env.ref("uom.product_uom_unit").id,
                company_id=company_id,
                type="product",
                **vals
            )
        )


class TestStockPickingType(TestStockRequest):
    def setUp(self):
        super(TestStockPickingType, self).setUp()

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
