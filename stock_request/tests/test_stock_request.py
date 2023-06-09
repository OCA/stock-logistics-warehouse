# Copyright 2017 ForgeFlow S.L.
# Copyright 2022 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from collections import Counter
from datetime import datetime

from odoo import exceptions, fields
from odoo.tests import common, new_test_user


class TestStockRequest(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # common models
        cls.stock_request = cls.env["stock.request"]
        cls.request_order = cls.env["stock.request.order"]
        # refs
        cls.stock_request_user_group = cls.env.ref(
            "stock_request.group_stock_request_user"
        )
        cls.main_company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.categ_unit = cls.env.ref("uom.product_uom_categ_unit")
        cls.virtual_loc = cls.env.ref("stock.stock_location_customers")
        # common data
        cls.company_2 = cls.env["res.company"].create(
            {"name": "Comp2", "parent_id": cls.main_company.id}
        )
        cls.company_2_address = (
            cls.env["res.partner"]
            .with_context(company_id=cls.company_2.id)
            .create({"name": "Peñiscola"})
        )
        cls.wh2 = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company_2.id)], limit=1
        )
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.stock_request_user = new_test_user(
            cls.env,
            login="stock_request_user",
            groups="stock_request.group_stock_request_user",
            company_ids=[(6, 0, [cls.main_company.id, cls.company_2.id])],
            context=ctx,
        )
        cls.stock_request_manager = new_test_user(
            cls.env,
            login="stock_request_manager",
            groups="stock_request.group_stock_request_manager",
            company_ids=[(6, 0, [cls.main_company.id, cls.company_2.id])],
            context=ctx,
        )
        cls.product = cls._create_product("SH", "Shoes", False)
        cls.product_company_2 = cls._create_product("SH_2", "Shoes", cls.company_2.id)
        cls.ressuply_loc = cls._create_location(
            name="Ressuply",
            location_id=cls.warehouse.view_location_id.id,
            company_id=cls.main_company.id,
        )
        cls.ressuply_loc_2 = cls._create_location(
            name="Ressuply",
            location_id=cls.wh2.view_location_id.id,
            company_id=cls.company_2.id,
        )
        cls.route = cls._create_location_route(
            name="Transfer", company_id=cls.main_company.id
        )
        cls.route_2 = cls._create_location_route(
            name="Transfer", company_id=cls.company_2.id
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
                "name": "Transfer",
                "route_id": cls.route_2.id,
                "location_src_id": cls.ressuply_loc_2.id,
                "location_id": cls.wh2.lot_stock_id.id,
                "action": "pull",
                "picking_type_id": cls.wh2.int_type_id.id,
                "procure_method": "make_to_stock",
                "warehouse_id": cls.wh2.id,
                "company_id": cls.company_2.id,
            }
        )
        cls.env["ir.config_parameter"].sudo().set_param(
            "stock.no_auto_scheduler", "True"
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
    def _create_location(cls, **vals):
        return cls.env["stock.location"].create(dict(usage="internal", **vals))

    @classmethod
    def _create_location_route(cls, **vals):
        return cls.env["stock.location.route"].create(
            dict(
                product_categ_selectable=False,
                product_selectable=True,
                sequence=10,
                **vals
            )
        )


class TestStockRequestBase(TestStockRequest):
    def test_defaults(self):
        vals = {
            "product_id": self.product.id,
            "product_uom_id": self.product.uom_id.id,
            "product_uom_qty": 5.0,
        }
        stock_request = (
            self.stock_request.with_user(self.stock_request_user)
            .with_context(company_id=self.main_company.id)
            .create(vals)
        )

        self.assertEqual(stock_request.requested_by, self.stock_request_user)

        self.assertEqual(stock_request.warehouse_id, self.warehouse)

        self.assertEqual(stock_request.location_id, self.warehouse.lot_stock_id)

    def test_defaults_order(self):
        vals = {}
        order = (
            self.request_order.with_user(self.stock_request_user)
            .with_context(company_id=self.main_company.id)
            .create(vals)
        )

        self.assertEqual(order.requested_by, self.stock_request_user)

        self.assertEqual(order.warehouse_id, self.warehouse)

        self.assertEqual(order.location_id, self.warehouse.lot_stock_id)

    def test_onchanges_order(self):
        expected_date = fields.Datetime.now()
        vals = {
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
        order = self.request_order.with_user(self.stock_request_user).new(vals)
        self.stock_request_user.company_id = self.company_2
        order.company_id = self.company_2

        order.onchange_company_id()

        stock_request = order.stock_request_ids
        self.assertEqual(order.warehouse_id, self.wh2)
        self.assertEqual(order.location_id, self.wh2.lot_stock_id)
        self.assertEqual(order.warehouse_id, stock_request.warehouse_id)

        procurement_group = self.env["procurement.group"].create({"name": "TEST"})
        order.procurement_group_id = procurement_group
        order.onchange_procurement_group_id()
        self.assertEqual(
            order.procurement_group_id, order.stock_request_ids.procurement_group_id
        )

        order.procurement_group_id = procurement_group
        order.onchange_procurement_group_id()
        self.assertEqual(
            order.procurement_group_id, order.stock_request_ids.procurement_group_id
        )
        order.picking_policy = "one"

        order.onchange_picking_policy()
        self.assertEqual(order.picking_policy, order.stock_request_ids.picking_policy)

        order.expected_date = datetime.now()
        order.onchange_expected_date()
        self.assertEqual(order.expected_date, order.stock_request_ids.expected_date)

        order.requested_by = self.stock_request_manager
        order.onchange_requested_by()
        self.assertEqual(order.requested_by, order.stock_request_ids.requested_by)

    def test_onchanges(self):
        self.product.route_ids = [(6, 0, self.route.ids)]
        vals = {
            "product_uom_id": self.product.uom_id.id,
            "product_uom_qty": 5.0,
            "company_id": self.main_company.id,
        }
        stock_request = self.stock_request.with_user(self.stock_request_user).new(vals)
        stock_request.product_id = self.product
        vals = stock_request.default_get(["warehouse_id", "company_id"])
        stock_request.update(vals)
        stock_request.onchange_product_id()
        self.assertIn(self.route.id, stock_request.route_ids.ids)

        self.stock_request_user.company_id = self.company_2
        stock_request.company_id = self.company_2
        stock_request.onchange_company_id()

        self.assertEqual(stock_request.warehouse_id, self.wh2)
        self.assertEqual(stock_request.location_id, self.wh2.lot_stock_id)

        product = self.env["product.product"].create(
            {
                "name": "Wheat",
                "uom_id": self.env.ref("uom.product_uom_kgm").id,
                "uom_po_id": self.env.ref("uom.product_uom_kgm").id,
            }
        )

        # Test onchange_product_id
        stock_request.product_id = product
        stock_request.onchange_product_id()

        self.assertEqual(
            stock_request.product_uom_id, self.env.ref("uom.product_uom_kgm")
        )

        stock_request.product_id = self.env["product.product"]

        # Test onchange_warehouse_id
        wh2_2 = (
            self.env["stock.warehouse"]
            .with_context(company_id=self.company_2.id)
            .create(
                {
                    "name": "C2_2",
                    "code": "C2_2",
                    "company_id": self.company_2.id,
                    "partner_id": self.company_2_address.id,
                }
            )
        )
        stock_request.warehouse_id = wh2_2
        stock_request.onchange_warehouse_id()

        self.assertEqual(stock_request.warehouse_id, wh2_2)

        self.stock_request_user.company_id = self.main_company
        stock_request.warehouse_id = self.warehouse
        stock_request.onchange_warehouse_id()

        self.assertEqual(stock_request.company_id, self.main_company)
        self.assertEqual(stock_request.location_id, self.warehouse.lot_stock_id)

    def test_stock_request_order_validations_01(self):
        """Testing the discrepancy in warehouse_id between
        stock request and order"""
        expected_date = fields.Datetime.now()
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.wh2.id,
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
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.with_user(self.stock_request_user).create(vals)

    def test_stock_request_order_validations_02(self):
        """Testing the discrepancy in location_id between
        stock request and order"""
        expected_date = fields.Datetime.now()
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.wh2.lot_stock_id.id,
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
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.with_user(self.stock_request_user).create(vals)

    def test_stock_request_order_validations_03(self):
        """Testing the discrepancy in requested_by between
        stock request and order"""
        expected_date = fields.Datetime.now()
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "requested_by": self.stock_request_user.id,
            "expected_date": expected_date,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "requested_by": self.stock_request_manager.id,
                        "company_id": self.main_company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.warehouse.lot_stock_id.id,
                        "expected_date": expected_date,
                    },
                )
            ],
        }
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.with_user(self.stock_request_user).create(vals)

    def test_stock_request_order_validations_04(self):
        """Testing the discrepancy in procurement_group_id between
        stock request and order"""
        procurement_group = self.env["procurement.group"].create(
            {"name": "Procurement"}
        )
        expected_date = fields.Datetime.now()
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "procurement_group_id": procurement_group.id,
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
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.with_user(self.stock_request_user).create(vals)

    def test_stock_request_order_validations_05(self):
        """Testing the discrepancy in company between
        stock request and order"""
        expected_date = fields.Datetime.now()
        vals = {
            "company_id": self.company_2.id,
            "warehouse_id": self.wh2.id,
            "location_id": self.wh2.lot_stock_id.id,
            "expected_date": expected_date,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "product_uom_qty": 5.0,
                        "company_id": self.company_2.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.warehouse.lot_stock_id.id,
                        "expected_date": expected_date,
                    },
                )
            ],
        }
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.with_user(self.stock_request_user).create(vals)

    def test_stock_request_order_validations_06(self):
        """Testing the discrepancy in expected dates between
        stock request and order"""
        expected_date = fields.Datetime.now()
        child_expected_date = "2015-01-01"
        vals = {
            "company_id": self.company_2.id,
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
                        "expected_date": child_expected_date,
                    },
                )
            ],
        }
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.create(vals)

    def test_stock_request_order_validations_07(self):
        """Testing the discrepancy in picking policy between
        stock request and order"""
        expected_date = fields.Datetime.now()
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "picking_policy": "one",
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
        with self.assertRaises(exceptions.ValidationError):
            self.request_order.with_user(self.stock_request_user).create(vals)

    def test_stock_request_validations_01(self):
        vals = {
            "product_id": self.product.id,
            "product_uom_id": self.env.ref("uom.product_uom_kgm").id,
            "product_uom_qty": 5.0,
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
        }
        # Select a UoM that is incompatible with the product's UoM
        with self.assertRaises(exceptions.ValidationError):
            self.stock_request.with_user(self.stock_request_user).create(vals)

    def test_create_request_01(self):
        expected_date = fields.Datetime.now()
        vals = {
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

        order = self.request_order.with_user(self.stock_request_user).create(vals)

        stock_request = order.stock_request_ids

        self.product.route_ids = [(6, 0, self.route.ids)]
        order.with_user(self.stock_request_manager).action_confirm()
        self.assertEqual(order.state, "open")
        self.assertEqual(stock_request.state, "open")

        self.assertEqual(len(order.picking_ids), 1)
        self.assertEqual(len(order.move_ids), 1)
        self.assertEqual(len(stock_request.picking_ids), 1)
        self.assertEqual(len(stock_request.move_ids), 1)
        self.assertEqual(
            stock_request.move_ids[0].location_dest_id, stock_request.location_id
        )
        self.assertEqual(stock_request.qty_in_progress, stock_request.product_uom_qty)
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.ressuply_loc.id,
                "quantity": 5.0,
            }
        )
        picking = stock_request.picking_ids[0]
        picking.with_user(self.stock_request_manager).action_confirm()
        self.assertEqual(stock_request.qty_in_progress, 5.0)
        self.assertEqual(stock_request.qty_done, 0.0)
        picking.with_user(self.stock_request_manager).action_assign()
        self.assertEqual(picking.origin, order.name)
        packout1 = picking.move_line_ids[0]
        packout1.qty_done = 5
        picking.with_user(self.stock_request_manager)._action_done()
        self.assertEqual(stock_request.qty_in_progress, 0.0)
        self.assertEqual(stock_request.qty_done, stock_request.product_uom_qty)
        self.assertEqual(order.state, "done")
        self.assertEqual(stock_request.state, "done")

    def test_create_request_02(self):
        """Use different UoM's"""

        vals = {
            "product_id": self.product.id,
            "product_uom_id": self.uom_dozen.id,
            "product_uom_qty": 1.0,
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
        }

        stock_request = self.stock_request.with_user(self.stock_request_user).create(
            vals
        )

        self.product.route_ids = [(6, 0, self.route.ids)]
        stock_request.with_user(self.stock_request_manager).action_confirm()
        self.assertEqual(stock_request.state, "open")
        self.assertEqual(len(stock_request.picking_ids), 1)
        self.assertEqual(len(stock_request.move_ids), 1)
        self.assertEqual(
            stock_request.move_ids[0].location_dest_id, stock_request.location_id
        )
        self.assertEqual(stock_request.qty_in_progress, stock_request.product_uom_qty)
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.ressuply_loc.id,
                "quantity": 12.0,
            }
        )
        picking = stock_request.picking_ids[0]
        picking.with_user(self.stock_request_manager).action_confirm()
        self.assertEqual(stock_request.qty_in_progress, 1.0)
        self.assertEqual(stock_request.qty_done, 0.0)
        picking.with_user(self.stock_request_manager).action_assign()
        packout1 = picking.move_line_ids[0]
        packout1.qty_done = 1
        picking.with_user(self.stock_request_manager)._action_done()
        self.assertEqual(stock_request.qty_in_progress, 0.0)
        self.assertEqual(stock_request.qty_done, stock_request.product_uom_qty)
        self.assertEqual(stock_request.state, "done")

    def test_create_request_03(self):
        """Multiple stock requests"""
        vals = {
            "product_id": self.product.id,
            "product_uom_id": self.product.uom_id.id,
            "product_uom_qty": 4.0,
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
        }

        stock_request_1 = (
            self.env["stock.request"].with_user(self.stock_request_user).create(vals)
        )
        stock_request_2 = (
            self.env["stock.request"]
            .with_user(self.stock_request_manager.id)
            .create(vals)
        )
        stock_request_2.product_uom_qty = 6.0
        self.product.route_ids = [(6, 0, self.route.ids)]
        stock_request_1.sudo().action_confirm()
        stock_request_2.sudo().action_confirm()
        self.assertEqual(len(stock_request_1.sudo().picking_ids), 1)
        self.assertEqual(
            stock_request_1.sudo().picking_ids, stock_request_2.sudo().picking_ids
        )
        self.assertEqual(
            stock_request_1.sudo().move_ids, stock_request_2.sudo().move_ids
        )
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.ressuply_loc.id,
                "quantity": 10.0,
            }
        )
        picking = stock_request_1.sudo().picking_ids[0]
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(stock_request_1.qty_in_progress, 4)
        self.assertEqual(stock_request_1.qty_done, 0)
        self.assertEqual(stock_request_1.qty_cancelled, 0)
        self.assertEqual(stock_request_2.qty_in_progress, 6)
        self.assertEqual(stock_request_2.qty_done, 0)
        self.assertEqual(stock_request_2.qty_cancelled, 0)
        packout1 = picking.move_line_ids[0]
        packout1.qty_done = 4
        self.env["stock.backorder.confirmation"].with_context(
            button_validate_picking_ids=[picking.id]
        ).create({"pick_ids": [(4, picking.id)]}).process_cancel_backorder()
        self.assertEqual(stock_request_1.qty_in_progress, 0)
        self.assertEqual(stock_request_1.qty_done, 4)
        self.assertEqual(stock_request_1.qty_cancelled, 0)
        self.assertEqual(stock_request_1.state, "done")
        self.assertEqual(stock_request_2.qty_in_progress, 0)
        self.assertEqual(stock_request_2.qty_done, 0)
        self.assertEqual(stock_request_2.qty_cancelled, 6)
        self.assertEqual(stock_request_2.state, "cancel")

    def test_cancel_request(self):
        expected_date = fields.Datetime.now()
        vals = {
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

        order = self.request_order.with_user(self.stock_request_user).create(vals)

        self.product.route_ids = [(6, 0, self.route.ids)]
        order.with_user(self.stock_request_manager).action_confirm()
        stock_request = order.stock_request_ids
        self.assertEqual(len(order.picking_ids), 1)
        self.assertEqual(len(order.move_ids), 1)
        self.assertEqual(len(stock_request.picking_ids), 1)
        self.assertEqual(len(stock_request.move_ids), 1)
        self.assertEqual(
            stock_request.move_ids[0].location_dest_id, stock_request.location_id
        )
        self.assertEqual(stock_request.qty_in_progress, stock_request.product_uom_qty)
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.ressuply_loc.id,
                "quantity": 5.0,
            }
        )
        picking = stock_request.picking_ids[0]
        picking.with_user(self.stock_request_user).action_confirm()
        self.assertEqual(stock_request.qty_in_progress, 5.0)
        self.assertEqual(stock_request.qty_done, 0.0)
        picking.with_user(self.stock_request_manager).action_assign()
        order.with_user(self.stock_request_manager).action_cancel()

        self.assertEqual(stock_request.qty_in_progress, 0.0)
        self.assertEqual(stock_request.qty_done, 0.0)
        self.assertEqual(len(stock_request.picking_ids), 0)

        # Set the request back to draft
        order.with_user(self.stock_request_user).action_draft()
        self.assertEqual(order.state, "draft")
        self.assertEqual(stock_request.state, "draft")

        # Re-confirm. We expect new pickings to be created
        order.with_user(self.stock_request_manager).action_confirm()
        self.assertEqual(len(stock_request.picking_ids), 1)
        self.assertEqual(len(stock_request.move_ids), 2)

    def test_view_actions(self):
        expected_date = fields.Datetime.now()
        vals = {
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

        order = self.request_order.create(vals)
        self.product.route_ids = [(6, 0, self.route.ids)]

        order.with_user(self.stock_request_manager).action_confirm()
        stock_request = order.stock_request_ids
        self.assertTrue(stock_request.picking_ids)
        self.assertTrue(order.picking_ids)

        action = order.action_view_transfer()
        self.assertEqual("domain" in action.keys(), True)
        self.assertEqual("views" in action.keys(), True)
        self.assertEqual(action["res_id"], order.picking_ids[0].id)

        action = order.action_view_stock_requests()
        self.assertEqual("domain" in action.keys(), True)
        self.assertEqual("views" in action.keys(), True)
        self.assertEqual(action["res_id"], stock_request[0].id)

        action = stock_request.action_view_transfer()
        self.assertEqual("domain" in action.keys(), True)
        self.assertEqual("views" in action.keys(), True)
        self.assertEqual(action["res_id"], stock_request.picking_ids[0].id)

        action = stock_request.picking_ids[0].action_view_stock_request()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_id"], stock_request.id)

    def test_stock_request_constrains(self):
        vals = {
            "product_id": self.product.id,
            "product_uom_id": self.product.uom_id.id,
            "product_uom_qty": 5.0,
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
        }

        stock_request = self.stock_request.with_user(self.stock_request_user).create(
            vals
        )

        # Cannot assign a warehouse that belongs to another company
        with self.assertRaises(exceptions.ValidationError):
            stock_request.warehouse_id = self.wh2
        # Cannot assign a product that belongs to another company
        with self.assertRaises(exceptions.ValidationError):
            stock_request.product_id = self.product_company_2
        # Cannot assign a location that belongs to another company
        with self.assertRaises(exceptions.ValidationError):
            stock_request.location_id = self.wh2.lot_stock_id
        # Cannot assign a route that belongs to another company
        with self.assertRaises(exceptions.ValidationError):
            stock_request.route_id = self.route_2

    def test_stock_request_order_from_products(self):
        product_a1 = self._create_product("CODEA1", "Product A1", self.main_company.id)
        template_a = product_a1.product_tmpl_id
        product_a2 = self._create_product(
            "CODEA2", "Product A2", self.main_company.id, product_tmpl_id=template_a.id
        )
        product_a3 = self._create_product(
            "CODEA3", "Product A3", self.main_company.id, product_tmpl_id=template_a.id
        )
        product_b1 = self._create_product("CODEB1", "Product B1", self.main_company.id)
        template_b = product_b1.product_tmpl_id
        # One archived variant of B
        self._create_product(
            "CODEB2",
            "Product B2",
            self.main_company.id,
            product_tmpl_id=template_b.id,
            active=False,
        )
        order = self.request_order

        # Selecting some variants and creating an order
        preexisting = order.search([])
        wanted_products = product_a1 + product_a2 + product_b1
        action = order._create_from_product_multiselect(wanted_products)
        new_order = order.search([]) - preexisting
        self.assertEqual(len(new_order), 1)
        self.assertEqual(
            action["res_id"],
            new_order.id,
            msg="Returned action references the wrong record",
        )
        self.assertEqual(
            Counter(wanted_products),
            Counter(new_order.stock_request_ids.mapped("product_id")),
            msg="Not all wanted products were ordered",
        )

        # Selecting a template and creating an order
        preexisting = order.search([])
        action = order._create_from_product_multiselect(template_a)
        new_order = order.search([]) - preexisting
        self.assertEqual(len(new_order), 1)
        self.assertEqual(
            action["res_id"],
            new_order.id,
            msg="Returned action references the wrong record",
        )
        self.assertEqual(
            Counter(product_a1 + product_a2 + product_a3),
            Counter(new_order.stock_request_ids.mapped("product_id")),
            msg="Not all of the template's variants were ordered",
        )

        # Selecting a template
        preexisting = order.search([])
        action = order._create_from_product_multiselect(template_a + template_b)
        new_order = order.search([]) - preexisting
        self.assertEqual(len(new_order), 1)
        self.assertEqual(
            action["res_id"],
            new_order.id,
            msg="Returned action references the wrong record",
        )
        self.assertEqual(
            Counter(product_a1 + product_a2 + product_a3 + product_b1),
            Counter(new_order.stock_request_ids.mapped("product_id")),
            msg="Inactive variant was ordered though it shouldn't have been",
        )

        # If a user does not have stock request rights, they can still trigger
        # the action from the products, so test that they get a friendlier
        # error message.
        self.stock_request_user.groups_id -= self.stock_request_user_group
        with self.assertRaisesRegex(
            exceptions.UserError,
            "Unfortunately it seems you do not have the necessary rights "
            "for creating stock requests. Please contact your "
            "administrator.",
        ):
            order.with_user(self.stock_request_user)._create_from_product_multiselect(
                template_a + template_b
            )

        # Empty recordsets should just return False
        self.assertFalse(
            order._create_from_product_multiselect(self.env["product.product"])
        )

        # Wrong model should just raise ValidationError
        with self.assertRaises(exceptions.ValidationError):
            order._create_from_product_multiselect(self.stock_request_user)

    def test_allow_virtual_location(self):
        self.main_company.stock_request_allow_virtual_loc = True
        vals = {
            "product_id": self.product.id,
            "product_uom_id": self.product.uom_id.id,
            "product_uom_qty": 5.0,
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.virtual_loc.id,
        }
        stock_request = self.stock_request.with_user(self.stock_request_user).create(
            vals
        )
        self.assertTrue(stock_request.allow_virtual_location)
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.virtual_loc.id,
        }
        order = self.request_order.with_user(self.stock_request_user).create(vals)
        self.assertTrue(order.allow_virtual_location)

    def test_onchange_wh_no_effect_from_order(self):
        expected_date = fields.Datetime.now()
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.virtual_loc.id,
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
                        "location_id": self.virtual_loc.id,
                        "expected_date": expected_date,
                    },
                )
            ],
        }
        order = self.request_order.with_user(self.stock_request_user).create(vals)
        order.stock_request_ids.onchange_warehouse_id()
        self.assertEqual(order.stock_request_ids[0].location_id, self.virtual_loc)

    def test_cancellation(self):
        group = self.env["procurement.group"].create({"name": "Procurement group"})
        product2 = self._create_product("SH2", "Shoes2", False)
        product3 = self._create_product("SH3", "Shoes3", False)
        self.product.type = "consu"
        product2.type = "consu"
        product3.type = "consu"
        vals = {
            "company_id": self.main_company.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.virtual_loc.id,
            "procurement_group_id": group.id,
            "stock_request_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_id": self.product.uom_id.id,
                        "procurement_group_id": group.id,
                        "product_uom_qty": 5.0,
                        "company_id": self.main_company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.virtual_loc.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": product2.id,
                        "product_uom_id": self.product.uom_id.id,
                        "procurement_group_id": group.id,
                        "product_uom_qty": 5.0,
                        "company_id": self.main_company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.virtual_loc.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": product3.id,
                        "product_uom_id": self.product.uom_id.id,
                        "procurement_group_id": group.id,
                        "product_uom_qty": 5.0,
                        "company_id": self.main_company.id,
                        "warehouse_id": self.warehouse.id,
                        "location_id": self.virtual_loc.id,
                    },
                ),
            ],
        }
        order = self.request_order.create(vals)
        self.product.route_ids = [(6, 0, self.route.ids)]
        product2.route_ids = [(6, 0, self.route.ids)]
        product3.route_ids = [(6, 0, self.route.ids)]
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(1, len(picking))
        picking.action_assign()
        self.assertEqual(3, len(picking.move_lines))
        line = picking.move_lines.filtered(lambda r: r.product_id == self.product)
        line.quantity_done = 1
        sr1 = order.stock_request_ids.filtered(lambda r: r.product_id == self.product)
        sr2 = order.stock_request_ids.filtered(lambda r: r.product_id == product2)
        sr3 = order.stock_request_ids.filtered(lambda r: r.product_id == product3)
        self.assertNotEqual(sr1.state, "done")
        self.assertNotEqual(sr2.state, "done")
        self.assertNotEqual(sr3.state, "done")
        self.env["stock.backorder.confirmation"].with_context(
            button_validate_picking_ids=[picking.id]
        ).create({"pick_ids": [(4, picking.id)]}).process()
        sr1.refresh()
        sr2.refresh()
        sr3.refresh()
        self.assertNotEqual(sr1.state, "done")
        self.assertNotEqual(sr2.state, "done")
        self.assertNotEqual(sr3.state, "done")
        picking = order.picking_ids.filtered(
            lambda r: r.state not in ["done", "cancel"]
        )
        self.assertEqual(1, len(picking))
        picking.action_assign()
        self.assertEqual(3, len(picking.move_lines))
        line = picking.move_lines.filtered(lambda r: r.product_id == self.product)
        line.quantity_done = 4
        line = picking.move_lines.filtered(lambda r: r.product_id == product2)
        line.quantity_done = 1
        self.env["stock.backorder.confirmation"].with_context(
            button_validate_picking_ids=[picking.id]
        ).create({"pick_ids": [(4, picking.id)]}).process_cancel_backorder()
        sr1.refresh()
        sr2.refresh()
        sr3.refresh()
        self.assertEqual(sr1.state, "done")
        self.assertEqual(sr1.qty_done, 5)
        self.assertEqual(sr1.qty_cancelled, 0)
        self.assertEqual(sr2.state, "cancel")
        self.assertEqual(sr2.qty_done, 1)
        self.assertEqual(sr2.qty_cancelled, 4)
        self.assertEqual(sr3.state, "cancel")
        self.assertEqual(sr3.qty_done, 0)
        self.assertEqual(sr3.qty_cancelled, 5)
