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
                "picking_type_id": picking_type.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
                "state": "confirmed",
            }
        )

    def _test_find_rule(self, pick_type, src_loc, dest_loc, method):
        routing = self.env["stock.routing"].create(
            {
                "location_id": pick_type.default_location_src_id.id
                if method == "pull"
                else pick_type.default_location_dest_id.id,
                "picking_type_id": pick_type.id,
            }
        )
        self.env["stock.routing.rule"].create(
            {
                "method": method,
                "routing_id": routing.id,
                "picking_type_id": pick_type.id,
                "sequence": 12,
            }
        )
        rule = self.env["stock.routing.rule"].create(
            {
                "method": method,
                "routing_id": routing.id,
                "picking_type_id": pick_type.id,
                "sequence": 10,
            }
        )

        move = self._create_stock_move(self.product, 10, pick_type)
        found_rule = self.env["stock.routing"]._find_rule_for_location(
            move, src_loc, dest_loc
        )
        self.assertEqual(found_rule, rule)

    def test_find_pull_rule(self):
        pick_type = self._create_picking_type(
            "A", self.location_shelf, self.suppliers_loc
        )
        self._test_find_rule(
            pick_type, self.location_shelf_1, self.customer_loc, "pull"
        )

    def test_find_push_rule(self):
        pick_type = self._create_picking_type(
            "A", self.suppliers_loc, self.location_shelf
        )
        self._test_find_rule(
            pick_type, self.customer_loc, self.location_shelf_1, "push"
        )

    def _test_find_rule_domain(self, src_loc, dest_loc, method):
        pick_type_a = self._create_picking_type("A", src_loc, dest_loc)
        routing = self.env["stock.routing"].create(
            {
                "location_id": src_loc.id if method == "pull" else dest_loc.id,
                "picking_type_id": pick_type_a.id,
            }
        )
        self.env["stock.routing.rule"].create(
            {
                "method": method,
                "routing_id": routing.id,
                "picking_type_id": pick_type_a.id,
                "sequence": 1,
                # rule not selected because of this:
                "rule_domain": [("product_id", "!=", self.product.id)],
            }
        )
        rule = self.env["stock.routing.rule"].create(
            {
                "method": method,
                "routing_id": routing.id,
                "picking_type_id": pick_type_a.id,
                "sequence": 10,
            }
        )

        move = self._create_stock_move(self.product, 10, pick_type_a)
        found_rule = self.env["stock.routing"]._find_rule_for_location(
            move, src_loc, dest_loc
        )
        self.assertEqual(found_rule, rule)

    def test_find_pull_rule_domain(self):
        self._test_find_rule_domain(self.location_shelf, self.customer_loc, "pull")

    def test_find_push_rule_domain(self):
        self._test_find_rule_domain(self.customer_loc, self.location_shelf, "push")

    def _test_find_picking_type(self, src_loc, dest_loc, method):
        pick_type_a = self._create_picking_type("A", src_loc, dest_loc)
        pick_type_b = self._create_picking_type("B", src_loc, dest_loc)
        routing = self.env["stock.routing"].create(
            {
                "location_id": src_loc.id if method == "pull" else dest_loc.id,
                # routing not selected because different pick type
                "picking_type_id": pick_type_a.id,
            }
        )
        self.env["stock.routing.rule"].create(
            {
                "method": method,
                "routing_id": routing.id,
                "picking_type_id": pick_type_a.id,
                "sequence": 1,
            }
        )
        routing = self.env["stock.routing"].create(
            {
                "location_id": src_loc.id if method == "pull" else dest_loc.id,
                # routing selected because same pick type
                "picking_type_id": pick_type_b.id,
            }
        )
        rule = self.env["stock.routing.rule"].create(
            {
                "method": method,
                "routing_id": routing.id,
                "picking_type_id": pick_type_b.id,
                "sequence": 10,
            }
        )
        move = self._create_stock_move(self.product, 10, pick_type_b)
        found_rule = self.env["stock.routing"]._find_rule_for_location(
            move, src_loc, dest_loc
        )
        self.assertEqual(found_rule, rule)

    def test_find_pull_picking_type(self):
        self._test_find_picking_type(self.location_shelf, self.suppliers_loc, "pull")

    def test_find_push_picking_type(self):
        self._test_find_picking_type(self.suppliers_loc, self.location_shelf, "push")
