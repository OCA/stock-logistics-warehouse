# Copyright 2016 Cyril Gaudin (Camptocamp)
# Copyright 2019 David Vidal - Tecnativa
# Copyright 2020 Víctor Martínez - Tecnativa
# Copyright 2024 Florian Mounier - Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models
from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestOrderpointGenerator(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_model = cls.env["stock.warehouse.orderpoint.generator"]
        cls.orderpoint_model = cls.env["stock.warehouse.orderpoint"]
        cls.orderpoint_template_model = cls.env["stock.warehouse.orderpoint.template"]
        cls.product_model = cls.env["product.product"]
        cls.p1 = cls.product_model.create({"name": "Unittest P1", "type": "product"})
        cls.p2 = cls.product_model.create({"name": "Unittest P2", "type": "product"})
        cls.wh1 = cls.env["stock.warehouse"].create(
            {"name": "TEST WH1", "code": "TST1"}
        )
        location_obj = cls.env["stock.location"]
        cls.supplier_loc = location_obj.create(
            {"name": "Test supplier location", "usage": "supplier"}
        )
        cls.customer_loc = location_obj.create(
            {"name": "Test customer location", "usage": "customer"}
        )
        cls.orderpoint_fields_dict = {
            "warehouse_id": cls.wh1.id,
            "location_id": cls.wh1.lot_stock_id.id,
            "name": "TEST-ORDERPOINT-001",
            "product_max_qty": 15.0,
            "product_min_qty": 5.0,
            "qty_multiple": 1,
        }
        cls.template = cls.orderpoint_template_model.create(cls.orderpoint_fields_dict)
        # Create some moves for p1 and p2 so we can have a history to test
        # p1 [100, 50, 45, 55, 52]
        # t1 - p1 - stock.move location1 100 # 100
        cls.p1m1 = cls.env["stock.move"].create(
            {
                "name": cls.p1.name,
                "product_id": cls.p1.id,
                "product_uom_qty": 100,
                "product_uom": cls.p1.uom_id.id,
                "location_id": cls.supplier_loc.id,
                "location_dest_id": cls.wh1.lot_stock_id.id,
                "state": "done",
                "date": "2019-01-01 01:00:00",
            }
        )
        cls.env["stock.move.line"].create(
            {
                "move_id": cls.p1m1.id,
                "product_id": cls.p1.id,
                "qty_done": 100,
                "product_uom_id": cls.p1.uom_id.id,
                "location_id": cls.supplier_loc.id,
                "location_dest_id": cls.wh1.lot_stock_id.id,
                "state": "done",
                "date": "2019-01-01 01:00:00",
            }
        )
        # t2 - p1 - stock.move location1 -50 # 50
        cls.p1m2 = cls.p1m1.copy(
            {
                "product_uom_qty": 50,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "state": "done",
                "date": "2019-01-01 02:00:00",
            }
        )
        cls.env["stock.move.line"].create(
            {
                "move_id": cls.p1m2.id,
                "product_id": cls.p1.id,
                "qty_done": 50,
                "product_uom_id": cls.p1.uom_id.id,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "state": "done",
                "date": "2019-01-01 02:00:00",
            }
        )
        # t3 - p1 - stock.move location1 -5 # 45
        cls.p1m3 = cls.p1m1.copy(
            {
                "name": cls.p1.name,
                "product_id": cls.p1.id,
                "product_uom_qty": 5,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "state": "done",
                "date": "2019-01-01 03:00:00",
            }
        )
        cls.env["stock.move.line"].create(
            {
                "move_id": cls.p1m3.id,
                "product_id": cls.p1.id,
                "qty_done": 5,
                "product_uom_id": cls.p1.uom_id.id,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "state": "done",
                "date": "2019-01-01 03:00:00",
            }
        )
        # t4 - p1 - stock.move location1 10 # 55
        cls.p1m4 = cls.p1m1.copy(
            {
                "product_uom_qty": 10,
                "location_id": cls.supplier_loc.id,
                "location_dest_id": cls.wh1.lot_stock_id.id,
                "state": "done",
                "date": "2019-01-01 04:00:00",
            }
        )
        cls.env["stock.move.line"].create(
            {
                "move_id": cls.p1m4.id,
                "product_id": cls.p1.id,
                "qty_done": 10,
                "product_uom_id": cls.p1.uom_id.id,
                "location_id": cls.supplier_loc.id,
                "location_dest_id": cls.wh1.lot_stock_id.id,
                "state": "done",
                "date": "2019-01-01 04:00:00",
            }
        )
        # t5 - p1 - stock.move location1 -3 # 52
        cls.p1m5 = cls.p1m1.copy(
            {
                "product_uom_qty": 3,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "state": "done",
                "date": "2019-01-01 05:00:00",
            }
        )
        cls.env["stock.move.line"].create(
            {
                "move_id": cls.p1m5.id,
                "product_id": cls.p1.id,
                "qty_done": 3,
                "product_uom_id": cls.p1.uom_id.id,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "state": "done",
                "date": "2019-01-01 05:00:00",
            }
        )
        # p2
        # t1 - p2 - stock.move location1 1000 # 1000
        cls.p2m1 = cls.env["stock.move"].create(
            {
                "name": cls.p2.name,
                "product_id": cls.p2.id,
                "product_uom": cls.p2.uom_id.id,
                "product_uom_qty": 1000,
                "location_id": cls.supplier_loc.id,
                "location_dest_id": cls.wh1.lot_stock_id.id,
                "state": "done",
                "date": "2019-01-01 01:00:00",
            }
        )
        cls.env["stock.move.line"].create(
            {
                "move_id": cls.p2m1.id,
                "product_id": cls.p2.id,
                "qty_done": 1000,
                "product_uom_id": cls.p2.uom_id.id,
                "location_id": cls.supplier_loc.id,
                "location_dest_id": cls.wh1.lot_stock_id.id,
                "state": "done",
                "date": "2019-01-01 01:00:00",
            }
        )
        # t2 - p2 - stock.move location1 -50 # 950
        cls.p2m2 = cls.p2m1.copy(
            {
                "product_uom_qty": 50,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "state": "done",
                "date": "2019-01-01 02:00:00",
            }
        )
        cls.env["stock.move.line"].create(
            {
                "move_id": cls.p2m2.id,
                "product_id": cls.p2.id,
                "qty_done": 50,
                "product_uom_id": cls.p2.uom_id.id,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "state": "done",
                "date": "2019-01-01 02:00:00",
            }
        )
        # t3 - p2 - stock.move location1 -7 # 943
        cls.p2m3 = cls.p2m1.copy(
            {
                "product_uom_qty": 7,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "state": "done",
                "date": "2019-01-01 03:00:00",
            }
        )
        cls.env["stock.move.line"].create(
            {
                "move_id": cls.p2m3.id,
                "product_id": cls.p2.id,
                "qty_done": 7,
                "product_uom_id": cls.p2.uom_id.id,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "state": "done",
                "date": "2019-01-01 03:00:00",
            }
        )
        # t4 - p2 - stock.move location1 100 # 1043
        cls.p2m4 = cls.p2m1.copy(
            {
                "product_uom_qty": 100,
                "location_id": cls.supplier_loc.id,
                "location_dest_id": cls.wh1.lot_stock_id.id,
                "state": "done",
                "date": "2019-01-01 04:00:00",
            }
        )
        cls.env["stock.move.line"].create(
            {
                "move_id": cls.p2m4.id,
                "product_id": cls.p2.id,
                "qty_done": 100,
                "product_uom_id": cls.p2.uom_id.id,
                "location_id": cls.supplier_loc.id,
                "location_dest_id": cls.wh1.lot_stock_id.id,
                "state": "done",
                "date": "2019-01-01 04:00:00",
            }
        )
        # t5 - p2 - stock.move location1 -3 # 1040
        cls.p2m5 = cls.p2m1.copy(
            {
                "product_uom_qty": 3,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "state": "done",
                "date": "2019-01-01 05:00:00",
            }
        )
        cls.env["stock.move.line"].create(
            {
                "move_id": cls.p2m5.id,
                "product_id": cls.p2.id,
                "qty_done": 3,
                "product_uom_id": cls.p2.uom_id.id,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "state": "done",
                "date": "2019-01-01 05:00:00",
            }
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        route_test = (
            cls.env["stock.location.route"].create({"name": "Stock to Test"}).id
        )
        cls.env["stock.rule"].create(
            {
                "name": "Stock to Test",
                "action": "pull_push",
                "procure_method": "make_to_stock",
                "location_id": cls.wh1.lot_stock_id.id,
                "location_src_id": cls.env.ref("stock.stock_location_suppliers").id,
                "route_id": route_test,
                "picking_type_id": cls.wh1.in_type_id.id,
                "warehouse_id": cls.wh1.id,
                "group_propagation_option": "none",
                "active": True,
            }
        )
        cls.productA = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "route_ids": [(6, 0, [route_test])],
            }
        )
        cls.productB = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
                "route_ids": [(6, 0, [route_test])],
            }
        )
        cls.productC = cls.env["product.product"].create(
            {
                "name": "Product C",
                "type": "product",
                "route_ids": [(6, 0, [route_test])],
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})

    def check_orderpoint(self, products, template, fields_dict):
        orderpoints = self.orderpoint_model.search(
            [("name", "=", template.name)], order="product_id"
        )
        self.assertEqual(len(products), len(orderpoints))
        for i, product in enumerate(products):
            self.assertEqual(product, orderpoints[i].product_id)
        for orderpoint in orderpoints:
            for field in fields_dict.keys():
                op_field_value = orderpoint[field]
                if isinstance(orderpoint[field], models.Model):
                    op_field_value = orderpoint[field].id
                self.assertEqual(op_field_value, fields_dict[field])
        return orderpoints

    def wizard_over_products(self, product, template):
        return self.wizard_model.with_context(
            active_model=product._name,
            active_ids=product.ids,
        ).create({"orderpoint_template_id": [(6, 0, template.ids)]})

    def test_product_orderpoint(self):
        products = self.p1 + self.p2
        wizard = self.wizard_over_products(products, self.template)
        wizard.action_configure()
        self.check_orderpoint(products, self.template, self.orderpoint_fields_dict)

    def test_template_orderpoint(self):
        prod_tmpl = self.p1.product_tmpl_id + self.p2.product_tmpl_id
        wizard = self.wizard_over_products(prod_tmpl, self.template)
        wizard.action_configure()
        products = self.p1 + self.p2
        self.check_orderpoint(products, self.template, self.orderpoint_fields_dict)

    def test_template_variants_orderpoint(self):
        self.product_model.create(
            {
                "product_tmpl_id": self.p1.product_tmpl_id.id,
                "name": "Unittest P1 variant",
            }
        )
        wizard = self.wizard_over_products(self.p1.product_tmpl_id, self.template)
        with self.assertRaises(UserError):
            wizard.action_configure()

    def test_auto_qty(self):
        """Compute min and max qty  according to criteria"""
        # Max stock for p1: 100
        self.template.write(
            {
                "auto_min_qty": True,
                "auto_min_date_start": "2019-01-01 01:30:00",
                "auto_min_date_end": "2019-02-01 00:00:00",
                "auto_min_qty_criteria": "max",
            }
        )
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict = self.orderpoint_fields_dict.copy()
        orderpoint_auto_dict.update({"product_min_qty": 100.0})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Min stock for p1: 45
        self.template.write({"auto_min_qty_criteria": "min"})
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_min_qty": 45.0})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Median of stock for p1: 52
        self.template.write({"auto_min_qty_criteria": "median"})
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_min_qty": 52.0})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Average of stock for p1: 60.4
        self.template.write({"auto_min_qty_criteria": "avg"})
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_min_qty": 60.4})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Set auto values for min and max: 60.4 (avg) 100 (max)
        self.template.write(
            {
                "auto_max_qty": True,
                "auto_max_date_start": "2019-01-01 00:00:00",
                "auto_max_date_end": "2019-02-01 00:00:00",
                "auto_max_qty_criteria": "max",
            }
        )
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_max_qty": 100})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # If they have the same values, only one is computed:
        self.template.write({"auto_min_qty_criteria": "max"})
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_min_qty": 100})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Auto min max over a shorter period
        self.template.write(
            {
                "auto_max_date_start": "2019-01-01 02:30:00",
                "auto_max_date_end": "2019-01-01 03:00:00",
                "auto_min_date_start": "2019-01-01 04:00:00",
                "auto_min_date_end": "2019-01-01 06:00:00",
            }
        )
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_min_qty": 55, "product_max_qty": 50})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Check delivered
        self.template.auto_min_qty_criteria = "delivered"
        self.template.auto_max_qty_criteria = "delivered"
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_min_qty": 3, "product_max_qty": 5})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)

    def test_auto_qty_multi_products(self):
        """Each product has a different history"""
        products = self.p1 + self.p2
        self.template.write(
            {
                "auto_min_qty": True,
                "auto_min_date_start": "2019-01-01 00:00:00",
                "auto_min_date_end": "2019-02-01 00:00:00",
                "auto_min_qty_criteria": "max",
            }
        )
        wizard = self.wizard_over_products(products, self.template)
        wizard.action_configure()
        orderpoint_auto_dict = self.orderpoint_fields_dict.copy()
        del orderpoint_auto_dict["product_min_qty"]
        orderpoints = self.check_orderpoint(
            products, self.template, orderpoint_auto_dict
        )
        self.assertEqual(orderpoints[0].product_min_qty, 100)
        self.assertEqual(orderpoints[1].product_min_qty, 1043)

    def test_stock_orderpoint_template_orderpoint_creation(self):
        warehouse = self.wh1

        template = self.env["stock.warehouse.orderpoint.template"].create(
            {
                "location_id": warehouse.lot_stock_id.id,
                "product_min_qty": 0.0,
                "product_max_qty": 15.0,
                "auto_add_product": True,
                "warehouse_id": warehouse.id,
            }
        )
        self.assertFalse(
            self.env["stock.warehouse.orderpoint"].search(
                [("product_id", "=", self.productA.id)]
            )
        )

        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": warehouse.out_type_id.id,
                "location_id": warehouse.lot_stock_id.id,
                "location_dest_id": self.ref("stock.stock_location_customers"),
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Delivery",
                            "product_id": self.productA.id,
                            "product_uom": self.uom_unit.id,
                            "product_uom_qty": 12.0,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()

        orderpoint = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", self.productA.id)]
        )

        self.assertTrue(orderpoint)
        self.assertEqual(orderpoint.orderpoint_template_id, template)
        self.assertEqual(orderpoint.product_min_qty, 0.0)
        self.assertEqual(orderpoint.product_max_qty, 15.0)
        self.assertEqual(orderpoint.warehouse_id, warehouse)
        self.assertEqual(orderpoint.location_id, warehouse.lot_stock_id)
        self.assertEqual(orderpoint.company_id, warehouse.company_id)
        self.assertEqual(orderpoint.trigger, "auto")

        receipt_move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.productA.id),
                ("location_id", "=", self.env.ref("stock.stock_location_suppliers").id),
            ]
        )
        self.assertTrue(receipt_move)
        self.assertEqual(receipt_move.product_uom_qty, 27.0)

    def test_stock_orderpoint_template_orderpoint_priority(self):
        warehouse = self.wh1

        self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.productA.id,
                "location_id": warehouse.lot_stock_id.id,
                "product_min_qty": 0.0,
                "product_max_qty": 5.0,
                "warehouse_id": warehouse.id,
            }
        )

        self.env["stock.warehouse.orderpoint.template"].create(
            {
                "location_id": warehouse.lot_stock_id.id,
                "product_min_qty": 0.0,
                "product_max_qty": 15.0,
                "auto_add_product": True,
                "warehouse_id": warehouse.id,
            }
        )

        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": warehouse.out_type_id.id,
                "location_id": warehouse.lot_stock_id.id,
                "location_dest_id": self.ref("stock.stock_location_customers"),
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Delivery",
                            "product_id": self.productA.id,
                            "product_uom": self.uom_unit.id,
                            "product_uom_qty": 12.0,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()

        receipt_move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.productA.id),
                ("location_id", "=", self.env.ref("stock.stock_location_suppliers").id),
            ]
        )
        self.assertTrue(receipt_move)
        self.assertEqual(receipt_move.product_uom_qty, 17.0)
