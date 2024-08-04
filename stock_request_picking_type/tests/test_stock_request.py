# Copyright 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo import fields
from odoo.tests import Form, common


class TestStockRequest(common.TransactionCase):
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
        cls.main_company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.default_picking_type = cls.env.ref(
            "stock_request_picking_type.stock_request_order"
        )

        # common data
        cls.company_2 = cls.env["res.company"].create(
            {"name": "Comp2", "parent_id": cls.main_company.id}
        )
        cls.company_2_address = (
            cls.env["res.partner"]
            .with_context(company_id=cls.company_2.id)
            .create({"name": "Peñiscola"})
        )

        cls.product = cls._create_product("SH", "Shoes", False)
        cls.product_company_2 = cls._create_product("SH_2", "Shoes", cls.company_2.id)
        cls.stock_request_user = cls._create_user(
            "stock_request_user",
            [cls.stock_request_user_group.id],
            [cls.main_company.id, cls.company_2.id],
        )


class TestStockRequestOrder(TestStockRequest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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

        stock_request_order_obj = self.env["stock.request.order"]
        vals = {
            "company_id": self.main_company.id,
            "expected_date": expected_date,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
        }
        stock_request_order_new = stock_request_order_obj.new(vals)

        # Test setting warehouse
        vals.update(
            stock_request_order_new.sudo()._convert_to_write(
                {
                    name: stock_request_order_new[name]
                    for name in stock_request_order_new._cache
                }
            )
        )
        vals.update({"warehouse_id": wh.id})
        stock_request_order = stock_request_order_obj.create(vals)

        self.assertEqual(stock_request_order.picking_type_id, new_pick_type)

    def test_create(self):
        expected_date = fields.Datetime.now()
        form = Form(
            self.request_order.with_context(allowed_company_ids=[self.main_company.id])
        )
        form.expected_date = expected_date

        # # test _getdefault_picking_type()
        self.assertEqual(form.picking_type_id, self.default_picking_type)
