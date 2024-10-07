# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestOrderpointGeneratorCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_model = cls.env["stock.warehouse.orderpoint.generator"]
        cls.orderpoint_model = cls.env["stock.warehouse.orderpoint"]
        cls.orderpoint_template_model = cls.env["stock.warehouse.orderpoint.template"]
        cls.product_model = cls.env["product.product"]
        cls.config_obj = cls.env["res.config.settings"]

        cls.p1 = cls.product_model.create({"name": "Unittest P1", "type": "product"})
        cls.p2 = cls.product_model.create({"name": "Unittest P2", "type": "product"})
        cls.p3 = cls.product_model.create({"name": "template T3", "type": "product"})
        cls.p4 = cls.product_model.create({"name": "template P4", "type": "product"})
        cls.p5 = cls.product_model.create({"name": "template P5", "type": "product"})
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

        cls.orderpoint_with_auto_products = {
            "warehouse_id": cls.wh1.id,
            "location_id": cls.wh1.lot_stock_id.id,
            "name": "TEST-ORDERPOINT-002",
            "product_max_qty": 15.0,
            "product_min_qty": 5.0,
            "qty_multiple": 1,
            "auto_generate": True,
            "trigger": "auto",
            "auto_product_ids": cls.p3.ids,
        }

        cls.orderpoint_with_use_domain = {
            "warehouse_id": cls.wh1.id,
            "location_id": cls.wh1.lot_stock_id.id,
            "name": "TEST-ORDERPOINT-003",
            "product_max_qty": 15.0,
            "product_min_qty": 5.0,
            "qty_multiple": 1,
            "auto_generate": True,
            "trigger": "auto",
            "domain": "[('name', 'ilike', 'template P')]",
        }

        cls.template = cls.orderpoint_template_model.create(cls.orderpoint_fields_dict)
        cls.template2 = cls.orderpoint_template_model.create(
            cls.orderpoint_with_auto_products
        )
        cls.template3 = cls.orderpoint_template_model.create(
            cls.orderpoint_with_use_domain
        )
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
