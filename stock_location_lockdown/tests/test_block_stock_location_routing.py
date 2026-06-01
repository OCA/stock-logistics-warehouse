# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .common import StockLocationLockdownCommon


class TestStockLocationLockdownRouting(StockLocationLockdownCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Two-step delivery (pick -> ship) so the route stages stock through an
        # intermediate Output location between Stock and the customer.
        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Lockdown WH",
                "code": "LKD",
                "delivery_steps": "pick_ship",
            }
        )
        cls.output_location = cls.warehouse.wh_output_stock_loc_id
        cls.Quant._update_available_quantity(
            cls.product, cls.warehouse.lot_stock_id, 50
        )

    def _run_delivery_procurement(self):
        """Procure the product at the customer through the warehouse delivery
        route. Returns the first (pick) move created by the run."""
        pg = self.env["procurement.group"].create({"name": "Lockdown routing"})
        self.env["procurement.group"].run(
            [
                pg.Procurement(
                    self.product,
                    5.0,
                    self.product.uom_id,
                    self.customer_location,
                    "lockdown",
                    "lockdown",
                    self.warehouse.company_id,
                    {"warehouse_id": self.warehouse, "group_id": pg},
                ),
            ]
        )
        return self.env["stock.move"].search([("group_id", "=", pg.id)])

    def _validate(self, move):
        move._action_assign()
        move.picked = True
        move._action_done()

    def test_blocked_rule_is_flagged(self):
        """The delivery rule leaving the blocked Output location is flagged."""
        self.output_location.block_stock_exit = True
        ship_rule = self.warehouse.delivery_route_id.rule_ids.filtered(
            lambda r: r.location_src_id == self.output_location
        )
        self.assertTrue(ship_rule)
        self.assertTrue(ship_rule.is_location_blocked)

    def test_chain_built_but_blocked_leg_unprocessable(self):
        """With Output outbound-blocked the two-step chain still builds
        normally (no crash): procurement creates the pick, validating it
        pushes the ship leg into existence. Only the ship leg, which leaves
        the blocked location, cannot be validated."""
        self.output_location.block_stock_exit = True

        pick = self._run_delivery_procurement()
        self.assertEqual(len(pick), 1)
        self.assertEqual(pick.location_id, self.warehouse.lot_stock_id)
        self.assertEqual(pick.location_dest_id, self.output_location)

        # Pick into Output is fine (outbound block does not block inbound); the
        # push rule then creates the ship leg.
        self._validate(pick)
        moves = self.env["stock.move"].search([("group_id", "=", pick.group_id.id)])
        self.assertEqual(len(moves), 2)
        ship = moves - pick
        self.assertEqual(ship.location_id, self.output_location)
        self.assertEqual(ship.location_dest_id, self.customer_location)

        # The ship leg leaves the blocked location: it cannot be validated.
        ship._action_assign()
        ship.picked = True
        with self.assertRaises(ValidationError):
            ship._action_done()
