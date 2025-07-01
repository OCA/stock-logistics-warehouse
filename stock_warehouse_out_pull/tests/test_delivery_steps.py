# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestDeliverySteps(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "TEST", "code": "TEST"}
        )
        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "TEST", "is_storable": True}
        )
        # Put some stock
        cls.env["stock.quant"]._update_available_quantity(
            cls.product,
            cls.warehouse.lot_stock_id,
            10,
        )

    def _run_procurement(self, product, qty):
        moves_before = self.env["stock.move"].search([])
        proc_group = self.env["procurement.group"]
        uom = product.uom_id
        proc_qty, proc_uom = uom._adjust_uom_quantities(qty, uom)
        today = fields.Date.today()
        proc_group = self.env["procurement.group"].create({})
        values = {
            "group_id": proc_group,
            "date_planned": today,
            "date_deadline": today,
            "warehouse_id": self.warehouse or False,
            "company_id": self.company,
        }
        procurement = proc_group.Procurement(
            product,
            proc_qty,
            proc_uom,
            self.customers_location,
            product.name,
            "PROC TEST",
            self.company,
            values,
        )
        proc_group.run([procurement])
        moves_after = self.env["stock.move"].search([])
        return moves_after - moves_before

    def _validate_picking(self, picking):
        picking.move_line_ids.write({"picked": True})
        picking._action_done()

    def test_delivery_pick_ship_with_pull_rules(self):
        """Test delivery pull rules with pick+ship configuration."""
        # Configure warehouse with pick+ship and delivery pull rules
        self.warehouse.write({"delivery_steps": "pick_ship", "delivery_pull": True})
        # Create chained delivery moves through a procurement
        moves = self._run_procurement(self.product, 10)
        # We get ship and pick moves
        self.assertEqual(len(moves), 2)
        ship_move, pick_move = moves
        self.assertEqual(ship_move.picking_type_id.code, "outgoing")
        self.assertEqual(ship_move.picking_type_id, self.warehouse.out_type_id)
        self.assertEqual(pick_move.picking_type_id.code, "internal")
        self.assertEqual(pick_move.picking_type_id, self.warehouse.pick_type_id)
        # Both are chained
        self.assertEqual(ship_move.move_orig_ids, pick_move)
        self.assertEqual(pick_move.move_dest_ids, ship_move)
        self.assertEqual(pick_move.state, "assigned")
        self.assertEqual(ship_move.state, "waiting")
        # Validating the first move makes the next one available
        self._validate_picking(pick_move.picking_id)
        self.assertEqual(pick_move.state, "done")
        self.assertEqual(ship_move.state, "assigned")
        self._validate_picking(ship_move.picking_id)
        self.assertEqual(ship_move.state, "done")

    def test_delivery_pick_pack_ship_with_pull_rules(self):
        """Test delivery pull rules with pick+pack+ship configuration."""
        # Configure warehouse with pick+ship and delivery pull rules
        self.warehouse.write(
            {"delivery_steps": "pick_pack_ship", "delivery_pull": True}
        )
        # Create chained delivery moves through a procurement
        moves = self._run_procurement(self.product, 10)
        # We get ship, pack and pick moves
        self.assertEqual(len(moves), 3)
        ship_move, pack_move, pick_move = moves
        self.assertEqual(ship_move.picking_type_id.code, "outgoing")
        self.assertEqual(ship_move.picking_type_id, self.warehouse.out_type_id)
        self.assertEqual(pack_move.picking_type_id.code, "internal")
        self.assertEqual(pack_move.picking_type_id, self.warehouse.pack_type_id)
        self.assertEqual(pick_move.picking_type_id.code, "internal")
        self.assertEqual(pick_move.picking_type_id, self.warehouse.pick_type_id)
        # All are chained
        self.assertEqual(ship_move.move_orig_ids, pack_move)
        self.assertEqual(pack_move.move_orig_ids, pick_move)
        self.assertEqual(pick_move.move_dest_ids, pack_move)
        self.assertEqual(pack_move.move_dest_ids, ship_move)
        self.assertEqual(pick_move.state, "assigned")
        self.assertEqual(pack_move.state, "waiting")
        self.assertEqual(ship_move.state, "waiting")
        # Validating the first move makes the next one available
        self._validate_picking(pick_move.picking_id)
        self.assertEqual(pick_move.state, "done")
        self.assertEqual(pack_move.state, "assigned")
        self.assertEqual(ship_move.state, "waiting")
        self._validate_picking(pack_move.picking_id)
        self.assertEqual(pack_move.state, "done")
        self.assertEqual(ship_move.state, "assigned")
        self._validate_picking(ship_move.picking_id)
        self.assertEqual(ship_move.state, "done")

    def test_delivery_multi_steps_toggle_delivery_pull(self):
        """First enable multi-steps delivery route, then enable delivery pull rules.

        Delivery route configuration should be updated accordingly.
        """
        # Configure warehouse with pick+ship at first...
        self.warehouse.delivery_steps = "pick_ship"
        # ...then enable delivery pull rules
        self.warehouse.delivery_pull = True
        # Create chained delivery moves through a procurement
        moves = self._run_procurement(self.product, 10)
        # We get ship and pick moves
        self.assertEqual(len(moves), 2)
        ship_move, pick_move = moves
        self.assertEqual(ship_move.picking_type_id.code, "outgoing")
        self.assertEqual(ship_move.picking_type_id, self.warehouse.out_type_id)
        self.assertEqual(pick_move.picking_type_id.code, "internal")
        self.assertEqual(pick_move.picking_type_id, self.warehouse.pick_type_id)
        # Both are chained
        self.assertEqual(ship_move.move_orig_ids, pick_move)
        self.assertEqual(pick_move.move_dest_ids, ship_move)
        self.assertEqual(pick_move.state, "assigned")
        self.assertEqual(ship_move.state, "waiting")
        # Validating the first move makes the next one available
        self._validate_picking(pick_move.picking_id)
        self.assertEqual(pick_move.state, "done")
        self.assertEqual(ship_move.state, "assigned")
        self._validate_picking(ship_move.picking_id)
        self.assertEqual(ship_move.state, "done")
