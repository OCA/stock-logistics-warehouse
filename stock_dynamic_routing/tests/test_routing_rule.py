# Copyright 2019 Camptocamp (https://www.camptocamp.com)

from odoo.tests import common


class TestRoutingRule(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )
        cls.suppliers_loc = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.wh = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "WHTEST",
            }
        )
        cls.location_shelf = cls.env["stock.location"].create(
            {"name": "Shelf", "location_id": cls.wh.lot_stock_id.id}
        )
        cls.location_shelf_1 = cls.env["stock.location"].create(
            {"name": "Shelf 1", "location_id": cls.location_shelf.id}
        )
        cls.location_shelf_2 = cls.env["stock.location"].create(
            {"name": "Shelf 2", "location_id": cls.location_shelf.id}
        )

    def _create_picking_type(self, name, src, dest):
        return self.env["stock.picking.type"].create(
            {
                "name": name,
                "code": "internal",
                "sequence_code": "WH/{}".format(name),
                "warehouse_id": self.wh.id,
                "use_create_lots": False,
                "use_existing_lots": True,
                "default_location_src_id": src.id,
                "default_location_dest_id": dest.id,
            }
        )

    def _create_stock_move(self, product, qty, picking_type):
        return self.env["stock.move"].create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
                "state": "confirmed",
            }
        )

    def test_find_pull_rule(self):
        pick_type_a = self._create_picking_type(
            "A", self.location_shelf, self.customer_loc
        )
        routing = self.env["stock.routing"].create(
            {"location_id": self.location_shelf.id}
        )
        self.env["stock.routing.rule"].create(
            {
                "method": "pull",
                "routing_id": routing.id,
                "picking_type_id": pick_type_a.id,
                "sequence": 12,
            }
        )
        rule = self.env["stock.routing.rule"].create(
            {
                "method": "pull",
                "routing_id": routing.id,
                "picking_type_id": pick_type_a.id,
                "sequence": 10,
            }
        )

        move = self._create_stock_move(self.product, 10, pick_type_a)
        found_rule = self.env["stock.routing"]._find_rule_for_location(
            move, self.location_shelf_1, self.customer_loc
        )
        self.assertEqual(found_rule, rule)

    def test_find_push_rule(self):
        pick_type_a = self._create_picking_type(
            "A", self.suppliers_loc, self.location_shelf
        )
        routing = self.env["stock.routing"].create(
            {"location_id": self.location_shelf.id}
        )
        self.env["stock.routing.rule"].create(
            {
                "method": "push",
                "routing_id": routing.id,
                "picking_type_id": pick_type_a.id,
                "sequence": 12,
            }
        )
        rule = self.env["stock.routing.rule"].create(
            {
                "method": "push",
                "routing_id": routing.id,
                "picking_type_id": pick_type_a.id,
                "sequence": 10,
            }
        )
        move = self._create_stock_move(self.product, 10, pick_type_a)
        found_rule = self.env["stock.routing"]._find_rule_for_location(
            move, self.suppliers_loc, self.location_shelf_1
        )
        self.assertEqual(found_rule, rule)

    def test_find_pull_rule_domain(self):
        pick_type_a = self._create_picking_type(
            "A", self.location_shelf, self.customer_loc
        )
        routing = self.env["stock.routing"].create(
            {"location_id": self.location_shelf.id}
        )
        self.env["stock.routing.rule"].create(
            {
                "method": "pull",
                "routing_id": routing.id,
                "picking_type_id": pick_type_a.id,
                "sequence": 1,
                # rule not selected because of this:
                "rule_domain": [("product_id", "!=", self.product.id)],
            }
        )
        rule = self.env["stock.routing.rule"].create(
            {
                "method": "pull",
                "routing_id": routing.id,
                "picking_type_id": pick_type_a.id,
                "sequence": 10,
            }
        )

        move = self._create_stock_move(self.product, 10, pick_type_a)
        found_rule = self.env["stock.routing"]._find_rule_for_location(
            move, self.location_shelf_1, self.customer_loc
        )
        self.assertEqual(found_rule, rule)

    def test_find_push_rule_domain(self):
        pick_type_a = self._create_picking_type(
            "A", self.suppliers_loc, self.location_shelf
        )
        routing = self.env["stock.routing"].create(
            {"location_id": self.location_shelf.id}
        )
        self.env["stock.routing.rule"].create(
            {
                "method": "push",
                "routing_id": routing.id,
                "picking_type_id": pick_type_a.id,
                "sequence": 1,
                # rule not selected because of this:
                "rule_domain": [("product_id", "!=", self.product.id)],
            }
        )
        rule = self.env["stock.routing.rule"].create(
            {
                "method": "push",
                "routing_id": routing.id,
                "picking_type_id": pick_type_a.id,
                "sequence": 10,
            }
        )
        move = self._create_stock_move(self.product, 10, pick_type_a)
        found_rule = self.env["stock.routing"]._find_rule_for_location(
            move, self.suppliers_loc, self.location_shelf_1
        )
        self.assertEqual(found_rule, rule)
