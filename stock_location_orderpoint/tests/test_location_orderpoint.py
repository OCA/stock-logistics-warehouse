# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime

from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase
from odoo.tools import mute_logger

from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.tests.common import trap_jobs


class TestLocationOrderpoint(TransactionCase):
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
        return self.env["stock.route"].create(
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
                            "location_dest_id": location_dest.id,
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

    def _create_incoming_move(self, qty, location):
        move = self._create_move(
            "Receive", qty, self.env.ref("stock.stock_location_suppliers"), location
        )
        move.move_line_ids.write({"qty_done": qty})
        move._action_done()
        return move

    def _create_outgoing_move(self, qty):
        return self._create_move(
            "Delivery",
            qty,
            self.location_dest,
            self.env.ref("stock.stock_location_customers"),
        )

    def _create_quants(self, product, location, qty):
        self.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "quantity": qty,
            }
        )

    def _run_replenishment(self, orderpoints):
        self.product.invalidate_recordset()
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

    def test_manual_replenishment(self):
        orderpoint, location_src = self._create_orderpoint_complete(
            "Stock2", trigger="manual"
        )
        orderpoint2, location_src2 = self._create_orderpoint_complete(
            "Stock2.2", trigger="manual"
        )

        self.assertEqual(orderpoint.location_src_id, location_src)
        move = self._create_outgoing_move(12)
        move = self._create_outgoing_move(1)
        self.assertEqual(move.state, "confirmed")

        orderpoints = orderpoint | orderpoint2
        self._run_replenishment(orderpoints)

        replenish_move = self._get_replenishment_move(orderpoints)
        self.assertFalse(replenish_move)

        self._create_quants(self.product, location_src, 12)

        self._run_replenishment(orderpoints)
        replenish_move = self._get_replenishment_move(orderpoints)
        self._check_replenishment_move(replenish_move, 12, orderpoint)

        replenish_move._action_cancel()

        self._create_quants(self.product, location_src2, 12)
        self._run_replenishment(orderpoints)

        replenish_moves = self._get_replenishment_move(orderpoints)
        self.assertEqual(len(replenish_moves), 2)
        self.assertEqual(sum(replenish_moves.mapped("product_qty")), 13)

        move = replenish_moves.filtered(
            lambda _move: _move.rule_id == orderpoint.route_id.rule_ids
        )
        self._check_replenishment_move(move, 12, orderpoint)

        move = replenish_moves - move
        self._check_replenishment_move(move, 1, orderpoint2)

    def test_check_unique(self):
        orderpoint, location_src = self._create_orderpoint_complete("Stock2")
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(IntegrityError):
                self._create_orderpoint(route_id=orderpoint.route_id)

    def test_check_constrains(self):
        with self.assertRaises(ValidationError):
            self._create_orderpoint(route_id=self.warehouse.delivery_route_id)

    def test_cron_replenishment(self):
        cron = self.env.ref("stock_location_orderpoint.ir_cron_location_replenishment")
        orderpoint, location_src = self._create_orderpoint_complete(
            "Stock2", trigger="cron"
        )
        self._create_outgoing_move(12)

        self.product.invalidate_recordset()
        cron.method_direct_trigger()

        replenish_move = self._get_replenishment_move(orderpoint)
        self.assertFalse(replenish_move)

        self._create_quants(self.product, location_src, 12)

        self.product.invalidate_recordset()
        cron.method_direct_trigger()

        replenish_move = self._get_replenishment_move(orderpoint)
        self._check_replenishment_move(replenish_move, 12, orderpoint)

    def test_auto_replenishment(self):
        job_func = self.env["stock.location.orderpoint"].run_auto_replenishment
        move_qty = 12
        with trap_jobs() as trap:
            move = self._create_outgoing_move(move_qty)
            trap.assert_jobs_count(1, only=job_func)
            trap.perform_enqueued_jobs()
            replenish_move = self.env["stock.move"].search(
                [
                    ("product_id", "=", move.product_id.id),
                    ("location_dest_id", "=", move.location_id.id),
                ]
            )
            self.assertFalse(replenish_move)

        orderpoint, location_src = self._create_orderpoint_complete(
            "Stock2", trigger="auto"
        )
        with trap_jobs() as trap:
            move = self._create_outgoing_move(move_qty)
            trap.assert_jobs_count(1, only=job_func)
            trap.assert_enqueued_job(
                orderpoint.run_auto_replenishment,
                args=(move.product_id, move.location_id, "location_id"),
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )
            self.product.invalidate_recordset()
            trap.perform_enqueued_jobs()
            replenish_move = self._get_replenishment_move(orderpoint)
            self.assertFalse(replenish_move)

        with trap_jobs() as trap:
            move = self._create_incoming_move(move_qty, location_src)
            trap.assert_jobs_count(1, only=job_func)
            trap.assert_enqueued_job(
                orderpoint.run_auto_replenishment,
                args=(move.product_id, move.location_dest_id, "location_src_id"),
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )
            self.product.invalidate_recordset()
            trap.perform_enqueued_jobs()
            replenish_move = self._get_replenishment_move(orderpoint)
            self._check_replenishment_move(replenish_move, move_qty, orderpoint)

        # Create a second incoming move so that the qty_available would be 24
        move = self._create_incoming_move(move_qty, location_src)
        with trap_jobs() as trap:
            move = self._create_outgoing_move(move_qty)
            trap.assert_jobs_count(1, only=job_func)
            trap.assert_enqueued_job(
                orderpoint.run_auto_replenishment,
                args=(move.product_id, move.location_id, "location_id"),
                kwargs={},
                properties=dict(
                    identity_key=identity_exact,
                ),
            )
            self.product.invalidate_recordset()
            trap.perform_enqueued_jobs()
            replenish_move_new = self._get_replenishment_move(orderpoint)
            self.assertEqual(replenish_move, replenish_move_new)
            self._check_replenishment_move(replenish_move, move_qty * 2, orderpoint)
