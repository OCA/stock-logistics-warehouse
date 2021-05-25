# Copyright 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo import fields
from odoo.tests import Form, common


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
        self.main_company = self.env.ref("base.main_company")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.default_picking_type = self.env.ref(
            "stock_request_picking_type.stock_request_order"
        )

        # common data
        self.company_2 = self.env["res.company"].create(
            {"name": "Comp2", "parent_id": self.main_company.id}
        )
        self.company_2_address = (
            self.env["res.partner"]
            .with_context(company_id=self.company_2.id)
            .create({"name": "Peñiscola"})
        )
        self.product = self._create_product("SH", "Shoes", False)
        self.product_company_2 = self._create_product(
            "SH_2", "Shoes", self.company_2.id
        )
        self.stock_request_user = self._create_user(
            "stock_request_user",
            [self.stock_request_user_group.id],
            [self.main_company.id, self.company_2.id],
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


class TestStockRequestOrder(TestStockRequest):
    def setUp(self):
        super(TestStockRequestOrder, self).setUp()

    def test_onchanges_order(self):
        expected_date = fields.Datetime.now()

        wh = (
            self.env["stock.warehouse"]
            .with_context(company_id=self.main_company.id)
            .create(
                {
                    "name": "Warehouse",
                    "code": "Warehouse",
                    "company_id": self.main_company.id,
                    "partner_id": self.main_company.id,
                }
            )
        )

        new_pick_type = (
            self.env["stock.picking.type"]
            .with_context(company_id=self.main_company.id)
            .create(
                {
                    "name": "Stock Request wh",
                    "sequence_id": self.env.ref(
                        "stock_request.seq_stock_request_order"
                    ).id,
                    "code": "stock_request_order",
                    "sequence_code": "SRO",
                    "warehouse_id": wh.id,
                }
            )
        )

        form = Form(self.env["stock.request.order"])
        form.company_id = self.main_company
        form.expected_date = expected_date
        form.warehouse_id = self.warehouse
        form.location_id = self.warehouse.lot_stock_id
        form.save()

        # Test onchange_warehouse_picking_id
        form.warehouse_id = wh
        form.save()

        self.assertEqual(form.picking_type_id, new_pick_type)

    def test_create(self):
        expected_date = fields.Datetime.now()
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

        form = Form(self.env["stock.request.order"])
        form.company_id = self.main_company
        form.expected_date = expected_date

        # test _getdefault_picking_type()
        self.assertEqual(form.picking_type_id, self.default_picking_type)

        form.warehouse_id = self.warehouse
        form.location_id = self.warehouse.lot_stock_id

        new_pick_type = (
            self.env["stock.picking.type"]
            .with_context(company_id=self.main_company.id)
            .create(
                {
                    "name": "Stock Request wh",
                    "sequence_id": self.env.ref(
                        "stock_request.seq_stock_request_order"
                    ).id,
                    "code": "stock_request_order",
                    "sequence_code": "SRO",
                    "warehouse_id": self.warehouse.id,
                }
            )
        )

        order = self.request_order.with_user(self.stock_request_user).create(order_vals)

        # test create()
        self.assertEqual(order.picking_type_id, new_pick_type)
