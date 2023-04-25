# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo.tests.common import Form, SavepointCase


class TestLocationOrderpointCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Desk Combination",
                "type": "product",
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location_dest = cls.warehouse.lot_stock_id
        cls.env["stock.location.orderpoint"].search([]).write({"active": False})

    def _create_picking_type(self, name, location_src, location_dest, warehouse):
        return self.env["stock.picking.type"].create(
            {
                "name": name,
                "sequence_code": f"INT/REPL/{location_src.name}",
                "default_location_src_id": location_src.id,
                "default_location_dest_id": location_dest.id,
                "code": "internal",
                "warehouse_id": warehouse.id,
                "show_operations": True,
            }
        )

    def _create_route(self, name, picking_type, location_src, location_dest, warehouse):
        return self.env["stock.location.route"].create(
            {
                "name": name,
                "sequence": 0,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": name,
                            "action": "pull",
                            "location_id": location_dest.id,
                            "location_src_id": location_src.id,
                            "picking_type_id": picking_type.id,
                            "warehouse_id": warehouse.id,
                        },
                    )
                ],
                "warehouse_ids": [(6, 0, warehouse.ids)],
            }
        )

    def _create_picking_type_route_rule(self, location):
        name = "Internal Replenishment"
        name = f"{name}-{location.name}"
        picking_type = self._create_picking_type(
            name, location, self.location_dest, self.warehouse
        )
        route = self._create_route(
            name, picking_type, location, self.location_dest, self.warehouse
        )
        return picking_type, route

    def _create_orderpoint(self, **kwargs):
        location_orderpoint = Form(self.env["stock.location.orderpoint"])
        location_orderpoint.location_id = self.location_dest
        for field, value in kwargs.items():
            setattr(location_orderpoint, field, value)
        return location_orderpoint.save()

    def _create_move(self, name, qty, location, location_dest):
        move = self.env["stock.move"].create(
            {
                "name": name,
                "date": datetime.today(),
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": qty,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
            }
        )
        move._write({"create_date": datetime.now()})
        move._action_confirm()
        return move

    def _create_scrap_move(self, qty, location):
        scrap = self.env["stock.location"].search(
            [("scrap_location", "=", True)], limit=1
        )
        move = self._create_move("Scrap", qty, location, scrap)
        move.move_line_ids.write({"qty_done": qty})
        move._action_done()
        return move

    def _create_incoming_move(self, qty, location):
        move = self._create_move(
            "Receive", qty, self.env.ref("stock.stock_location_suppliers"), location
        )
        move.move_line_ids.write({"qty_done": qty})
        move._action_done()
        return move

    def _create_outgoing_move(self, qty, location=None):
        move = self._create_move(
            "Delivery",
            qty,
            location or self.location_dest,
            self.env.ref("stock.stock_location_customers"),
        )
        move._action_assign()
        return move

    def _create_quants(self, product, location, qty):
        self.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "quantity": qty,
            }
        )

    def _run_replenishment(self, orderpoints):
        self.product.invalidate_cache()
        orderpoints.run_replenishment()

    def _get_replenishment_move(self, orderpoints):
        return self.env["stock.move"].search(
            [
                ("origin", "in", orderpoints.mapped("name")),
                ("product_id", "=", self.product.id),
                ("state", "!=", "cancel"),
            ]
        )

    def _check_replenishment_move(self, move, qty, orderpoint):
        self.assertEqual(move.rule_id, orderpoint.route_id.rule_ids)
        self.assertEqual(move.location_orderpoint_id, orderpoint)
        self.assertEqual(move.product_qty, qty)
        self.assertEqual(move.location_id, orderpoint.location_src_id)
        self.assertEqual(move.location_dest_id, orderpoint.location_id)
        self.assertEqual(move.state, "assigned")
        self.assertEqual(move.priority, orderpoint.priority)

    def _create_location(self, name):
        return self.env["stock.location"].create(
            {"name": name, "location_id": self.location_dest.location_id.id}
        )

    def _create_orderpoint_complete(self, location_name, **kwargs):
        location = self._create_location(location_name)
        picking_type, route = self._create_picking_type_route_rule(location)
        values = kwargs or {}
        values.update({"route_id": route})
        orderpoint = self._create_orderpoint(**values)
        return orderpoint, location
