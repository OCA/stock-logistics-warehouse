# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo.tests.common as common


class TestProcurementOrder(common.SavepointCase):

    @classmethod
    def _create_product(cls):
        # Create new product
        vals = {
            'name': 'Product Purchase Pack Test',
            'categ_id': cls.env.ref('product.product_category_5').id,
            'list_price': 30.0,
            'standard_price': 20.0,
            'type': 'product',
            'uom_id': cls.env.ref('product.product_uom_unit').id,

        }
        cls.product_test = cls.product_obj.create(vals)
        cls.unit_pair = cls.env["product.uom"].create({
            "category_id": cls.env.ref("product.product_uom_categ_unit").id,
            "name": "Pair",
            "factor_inv": 2.0,
            "uom_type": "bigger",
            "rounding": 1.0
        })
        cls.product_packaging_2 = cls.env['product.packaging'].create({
            'product_tmpl_id': cls.product_test.product_tmpl_id.id,
            'uom_id': cls.unit_pair.id,
            'name': 'Packaging Pair'
        })
        # Create supplierinfo for purchase
        vals = {
            "name": cls.env.ref("base.res_partner_2").id,
            "product_tmpl_id": cls.product_test.product_tmpl_id.id,
            "min_qty_uom_id": cls.unit_pair.id,
            "min_qty": 1.0,
        }
        cls.supplierinfo = cls.env["product.supplierinfo"].create(vals)

    @classmethod
    def _create_warehouse(cls):
        """
            Create two warehouses (a Main one and a second)

        """
        vals = {
            "name": "Main Warehouse Test",
            "code": "MAIN",
        }
        cls.main_warehouse = cls.warehouse_obj.create(vals)
        vals = {
            "name": "Second Warehouse Test",
            "code": "SECOND",
        }
        cls.second_warehouse = cls.warehouse_obj.create(vals)

    @classmethod
    def _create_resupply_route(cls):
        vals = {
            "name": "Picking Type Resupply Second",
            "code": "outgoing",
            "default_location_src_id": cls.main_warehouse.lot_stock_id.id,
            "default_location_dest_id": cls.second_warehouse.lot_stock_id.id,
            "sequence_id": cls.env.ref('stock.seq_picking_internal').id,
        }
        cls.picking_type_resupply = cls.picking_type_obj.create(vals)
        vals = {
            "name": "Route Resuply SECOND"
        }
        cls.route_resupply = cls.route_obj.create(vals)
        vals = {
            "name": "Resupply Second Stock",
            "action": "move",
            "location_id": cls.second_warehouse.lot_stock_id.id,
            "location_src_id": cls.main_warehouse.lot_stock_id.id,
            "procure_method": "make_to_stock",
            "warehouse_id": cls.second_warehouse.id,
            "route_id": cls.route_resupply.id,
            "picking_type_id": cls.picking_type_resupply.id,
        }
        cls.rule_obj.create(vals)

    @classmethod
    def _create_orderpoint(cls):
        """
            Create orderpoint for main warehouse
        """
        vals = {
            "name": "Internal Transfers",
        }
        cls.group_internal = cls.env["procurement.group"].create(vals)
        vals = {
            "product_id": cls.product_test.id,
            "location_id": cls.main_warehouse.lot_stock_id.id,
            "product_min_qty": 1.0,
            "product_max_qty": 1.0,
            "group_id": False,
            "warehouse_id": cls.main_warehouse.id,
        }
        cls.orderpoint = cls.orderpoint_obj.create(vals)

        vals = {
            "product_id": cls.product_test.id,
            "location_id": cls.second_warehouse.lot_stock_id.id,
            "product_min_qty": 1.0,
            "product_max_qty": 1.0,
            "group_id": cls.group_internal.id,
            "warehouse_id": cls.second_warehouse.id,
        }
        cls.second_orderpoint = cls.orderpoint_obj.create(vals)

    @classmethod
    def setUpClass(cls):
        super(TestProcurementOrder, cls).setUpClass()
        cls.warehouse_obj = cls.env["stock.warehouse"]
        cls.route_obj = cls.env["stock.location.route"]
        cls.rule_obj = cls.env["procurement.rule"]
        cls.orderpoint_obj = cls.env["stock.warehouse.orderpoint"]
        cls.picking_type_obj = cls.env["stock.picking.type"]
        cls.product_obj = cls.env['product.product']
        cls.purchase_obj = cls.env["purchase.order"]
        cls.purchase_line_obj = cls.env["purchase.order.line"]
        cls.procurement_obj = cls.env["procurement.order"]
        cls.move_obj = cls.env["stock.move"]

        cls._create_product()
        cls._create_warehouse()
        cls._create_resupply_route()
        cls._create_orderpoint()

        cls.product_test.route_ids |= cls.route_resupply | \
            cls.second_warehouse.buy_pull_id.route_id

    def test_orderpoint(self):
        """
            Product is with stock quantity == 0 in both stocks
            Run the scheduler
            A move from MAIN > SECOND warehouse should be generated
            A purchase with product_qty == 2.0 should be generated
            Run the scheduler
            Move and purchase shouldn't have changed
        """
        line = self.purchase_line_obj.search([
            ("product_id", "=", self.product_test.id)])
        self.assertFalse(line)

        self.assertFalse(self.product_test.virtual_available)
        self.procurement_obj.run_scheduler()
        line = self.purchase_line_obj.search([
            ("product_id", "=", self.product_test.id)])
        self.assertTrue(
            line
        )
        self.assertEqual(
            2.0,
            line.product_qty
        )
        move = self.move_obj.search([
            ("product_id", "=", self.product_test.id),
            ("location_dest_id", "=", self.second_warehouse.lot_stock_id.id)])

        self.assertEqual(
            1,
            len(move)
        )
        self.procurement_obj.run_scheduler()

        move = self.move_obj.search([
            ("product_id", "=", self.product_test.id),
            ("location_dest_id", "=", self.second_warehouse.lot_stock_id.id)])

        self.assertEqual(
            1,
            len(move)
        )

        line = self.purchase_line_obj.search([
            ("product_id", "=", self.product_test.id)])
        self.assertEqual(
            2.0,
            sum(line.mapped("product_qty"))
        )

        self.procurement_obj.run_scheduler()

        move = self.move_obj.search([
            ("product_id", "=", self.product_test.id),
            ("location_dest_id", "=", self.second_warehouse.lot_stock_id.id)])

        self.assertEqual(
            1,
            len(move)
        )

        line = self.purchase_line_obj.search([
            ("product_id", "=", self.product_test.id)])
        self.assertEqual(
            2.0,
            sum(line.mapped("product_qty"))
        )
        self.procurement_obj.run_scheduler()

        line = self.purchase_line_obj.search([
            ("product_id", "=", self.product_test.id)])
        self.assertEqual(
            2.0,
            sum(line.mapped("product_qty"))
        )
