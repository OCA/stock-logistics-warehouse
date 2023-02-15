# Copyright 2017-2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields
from odoo.tests.common import TransactionCase

from ..hooks import uninstall_hook


class TestStockRequestSubmit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Model
        cls.StockRequest = cls.env["stock.request"]
        cls.StockRequestOrder = cls.env["stock.request.order"]
        cls.StockLocation = cls.env["stock.location"]
        cls.StockLocationRoute = cls.env["stock.location.route"]
        cls.StockRule = cls.env["stock.rule"]
        cls.ProductProduct = cls.env["product.product"]
        cls.ResUsers = cls.env["res.users"]

        # Data
        cls.expected_date = fields.Datetime.now()
        cls.main_company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_request_user_group = cls.env.ref(
            "stock_request.group_stock_request_user"
        )
        cls.stock_request_manager_group = cls.env.ref(
            "stock_request.group_stock_request_manager"
        )
        cls.ressuply_loc = cls.StockLocation.create(
            {
                "name": "Ressuply",
                "location_id": cls.warehouse.view_location_id.id,
                "usage": "internal",
                "company_id": cls.main_company.id,
            }
        )
        cls.route = cls.StockLocationRoute.create(
            {
                "name": "Transfer",
                "product_categ_selectable": False,
                "product_selectable": True,
                "company_id": cls.main_company.id,
                "sequence": 10,
            }
        )
        cls.rule = cls.StockRule.create(
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
        cls.product = cls.ProductProduct.create(
            {
                "name": "test product",
                "type": "product",
                "route_ids": [(6, 0, cls.route.ids)],
            }
        )
        cls.stock_request_user = cls.ResUsers.create(
            {
                "name": "Stock Request User",
                "login": "stock_request_user",
                "groups_id": [(6, 0, [cls.stock_request_user_group.id])],
            }
        )
        cls.stock_request_manager = cls.ResUsers.create(
            {
                "name": "Stock Request Manager",
                "login": "stock_request_manager",
                "groups_id": [(6, 0, [cls.stock_request_manager_group.id])],
            }
        )

        vals = {
            "company_id": cls.main_company.id,
            "warehouse_id": cls.warehouse.id,
            "location_id": cls.warehouse.lot_stock_id.id,
            "expected_date": cls.expected_date,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": cls.product.id,
                        "product_uom_id": cls.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "company_id": cls.main_company.id,
                        "warehouse_id": cls.warehouse.id,
                        "location_id": cls.warehouse.lot_stock_id.id,
                        "expected_date": cls.expected_date,
                    },
                )
            ],
        }
        cls.order = cls.StockRequestOrder.with_user(cls.stock_request_user).create(vals)
        cls.stock_request = cls.order.stock_request_ids

    def test_stock_request_submit(self):
        self.order.action_submit()
        self.assertEqual(self.order.state, "submitted")
        self.assertEqual(self.stock_request.state, "submitted")
        self.order.with_user(self.stock_request_manager).action_confirm()
        self.assertEqual(self.order.state, "open")
        self.assertEqual(self.stock_request.state, "open")

    def test_uninstall_hook(self):
        # Check state before uninstall
        self.order.action_submit()
        self.assertEqual(self.order.state, "submitted")
        self.assertEqual(self.stock_request.state, "submitted")

        # Uninstall this module
        uninstall_hook(self.cr, self.registry)

        # Check state after uninstall
        self.assertEqual(self.order.state, "draft")
        self.assertEqual(self.stock_request.state, "draft")
