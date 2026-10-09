# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from datetime import timedelta

from odoo import fields
from odoo.tests import new_test_user
from odoo.tools import mute_logger

from odoo.addons.stock_vertical_lift.tests.common import VerticalLiftCase

SHUTTLE_LOGGER = "odoo.addons.stock_vertical_lift.models.vertical_lift_shuttle"


class TestPickPriority(VerticalLiftCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The demo outgoing transfer would be listed on the shuttle too
        cls.env.ref(
            "stock_vertical_lift.stock_picking_out_demo_vertical_lift_1"
        ).action_cancel()
        cls.shelf = cls.env["stock.location"].create(
            {"name": "Shelf", "location_id": cls.stock_location.id}
        )
        cls._update_qty_in_location(cls.location_1a_x1y1, cls.product_socks, 100)
        cls._update_qty_in_location(cls.location_1a_x2y1, cls.product_recovery, 100)
        # Deliveries must not reserve the shuttle's goods themselves
        cls.env.ref("stock.picking_type_out").reservation_method = "manual"
        cls.env.company.vertical_lift_pick_by_priority = True
        cls.env.company.vertical_lift_pick_skipped_last = True

    @classmethod
    def _create_replenishments(cls):
        """Two ready internal transfers taking goods out of the shuttle.

        Without any demand, the socks come first: their transfer is scheduled
        earlier. A test expecting the recovery socks first proves the demand
        was taken into account.
        """
        socks = cls._create_replenishment(cls.product_socks, days=0)
        recovery = cls._create_replenishment(cls.product_recovery, days=1)
        return socks, recovery

    @classmethod
    def _create_replenishment(cls, product, quantity=1, days=0):
        """Internal transfer taking goods out of the shuttle, ready to pick"""
        picking_type = cls.env.ref("stock.picking_type_internal")
        picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": cls.shuttle.location_id.id,
                "location_dest_id": cls.shelf.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": quantity,
                            "location_id": cls.shuttle.location_id.id,
                            "location_dest_id": cls.shelf.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.scheduled_date = fields.Datetime.now() + timedelta(days=days)
        return picking

    @classmethod
    def _create_delivery(cls, product, priority="0", days=0, quantity=1):
        """Confirmed delivery waiting for goods, not reserved on the shuttle"""
        picking = cls._create_simple_picking_out(product, quantity)
        picking.priority = priority
        picking.action_confirm()
        picking.move_ids.date = fields.Datetime.now() + timedelta(days=days)
        return picking

    def _assert_pick_order(self, *pickings):
        operation = self._open_screen("pick")
        for picking in pickings:
            self.assertEqual(operation.current_move_line_id.picking_id, picking)
            operation.select_next_move_line()

    @mute_logger(SHUTTLE_LOGGER)
    def test_unchained_demand_priority(self):
        """The line awaited by the urgent delivery comes first"""
        socks, recovery = self._create_replenishments()
        self._create_delivery(self.product_socks, priority="0")
        self._create_delivery(self.product_recovery, priority="1")
        self._assert_pick_order(recovery, socks)

    @mute_logger(SHUTTLE_LOGGER)
    def test_unchained_demand_date(self):
        """Same priority: the line awaited by the earliest delivery first"""
        socks, recovery = self._create_replenishments()
        self._create_delivery(self.product_socks, days=2)
        self._create_delivery(self.product_recovery, days=1)
        self._assert_pick_order(recovery, socks)

    @mute_logger(SHUTTLE_LOGGER)
    def test_unchained_demand_ignores_other_states(self):
        """Done, cancelled and draft deliveries are not a demand"""
        socks, recovery = self._create_replenishments()
        self._create_delivery(self.product_socks, priority="1").action_cancel()
        draft = self._create_simple_picking_out(self.product_socks, 1)
        draft.priority = "1"
        self._create_delivery(self.product_recovery, priority="0")
        self._assert_pick_order(recovery, socks)

    @mute_logger(SHUTTLE_LOGGER)
    def test_chained_demand_wins_over_product_search(self):
        """A chained delivery decides, even if a more urgent one exists"""
        socks, recovery = self._create_replenishments()
        chained = self._create_delivery(self.product_socks, priority="0", days=3)
        socks.move_ids.move_dest_ids = chained.move_ids
        self._create_delivery(self.product_socks, priority="1")
        self._create_delivery(self.product_recovery, priority="0", days=1)
        self._assert_pick_order(recovery, socks)

    @mute_logger(SHUTTLE_LOGGER)
    def test_chained_demand_priority(self):
        """Chained: the line feeding the urgent delivery comes first"""
        socks, recovery = self._create_replenishments()
        socks.move_ids.move_dest_ids = self._create_delivery(
            self.product_socks, priority="0"
        ).move_ids
        recovery.move_ids.move_dest_ids = self._create_delivery(
            self.product_recovery, priority="1"
        ).move_ids
        self._assert_pick_order(recovery, socks)

    @mute_logger(SHUTTLE_LOGGER)
    def test_no_demand_keeps_transfer_order(self):
        """Without any delivery, the transfer's own priority still applies"""
        socks, recovery = self._create_replenishments()
        recovery.priority = "1"
        self._assert_pick_order(recovery, socks)

    @mute_logger(SHUTTLE_LOGGER)
    def test_skipped_last(self):
        """A skipped line waits for the others, even when its demand is urgent"""
        socks, recovery = self._create_replenishments()
        self._create_delivery(self.product_recovery, priority="1")
        recovery.move_line_ids.vertical_lift_skipped = True
        self._assert_pick_order(socks, recovery)

    @mute_logger(SHUTTLE_LOGGER)
    def test_priority_setting_disabled(self):
        """Without the setting, deliveries are not looked at"""
        socks, recovery = self._create_replenishments()
        self._create_delivery(self.product_recovery, priority="1")
        self.env.company.vertical_lift_pick_by_priority = False
        self._assert_pick_order(socks, recovery)

    @mute_logger(SHUTTLE_LOGGER)
    def test_skipped_oldest_first(self):
        """Among skipped lines, the oldest skip comes first, whatever the demand"""
        socks, recovery = self._create_replenishments()
        self._create_delivery(self.product_recovery, priority="1")
        socks.move_line_ids.vertical_lift_skipped_date = "2026-01-01 10:00:00"
        recovery.move_line_ids.vertical_lift_skipped_date = "2026-01-02 10:00:00"
        self._assert_pick_order(socks, recovery)

    @mute_logger(SHUTTLE_LOGGER)
    def test_priority_raise_unskips_awaited_line(self):
        """Raising a delivery's priority proposes its skipped line again"""
        socks, recovery = self._create_replenishments()
        delivery = self._create_delivery(self.product_socks)
        self._create_delivery(self.product_recovery, days=1)
        operation = self._open_screen("pick")
        self.assertEqual(operation.current_move_line_id.picking_id, socks)
        operation.button_skip()
        self.assertEqual(operation.current_move_line_id.picking_id, recovery)
        self.assertTrue(socks.move_line_ids.vertical_lift_skipped_date)

        delivery.priority = "1"
        self.assertFalse(socks.move_line_ids.vertical_lift_skipped_date)
        operation.select_next_move_line()
        self.assertEqual(operation.current_move_line_id.picking_id, socks)

    @mute_logger(SHUTTLE_LOGGER)
    def test_priority_raise_without_vertical_lift_access(self):
        """A user without access to the shuttle can raise a delivery's priority"""
        socks, recovery = self._create_replenishments()
        delivery = self._create_delivery(self.product_socks)
        operation = self._open_screen("pick")
        operation.button_skip()
        self.assertTrue(socks.move_line_ids.vertical_lift_skipped_date)
        group = self.env["res.groups"].create(
            {
                "name": "Transfers only",
                "model_access": [
                    (
                        0,
                        0,
                        {
                            "name": "Transfers only",
                            "model_id": self.env.ref("stock.model_stock_picking").id,
                            "perm_read": True,
                            "perm_write": True,
                        },
                    )
                ],
            }
        )
        user = new_test_user(
            self.env,
            login="transfers_only",
            groups_id=[self.env.ref("base.group_user").id, group.id],
        )
        self.assertFalse(user.has_group("stock.group_stock_user"))

        delivery.with_user(user).priority = "1"
        self.assertFalse(socks.move_line_ids.vertical_lift_skipped_date)

    @mute_logger(SHUTTLE_LOGGER)
    def test_priority_decrease_keeps_skip(self):
        """Lowering a delivery's priority leaves the skipped line alone"""
        socks, recovery = self._create_replenishments()
        delivery = self._create_delivery(self.product_socks, priority="1")
        operation = self._open_screen("pick")
        operation.button_skip()
        self.assertTrue(socks.move_line_ids.vertical_lift_skipped_date)

        delivery.priority = "0"
        self.assertTrue(socks.move_line_ids.vertical_lift_skipped_date)

    @mute_logger(SHUTTLE_LOGGER)
    def test_priority_raise_other_delivery_keeps_skip(self):
        """A raised delivery not waiting for the line leaves it skipped"""
        socks, recovery = self._create_replenishments()
        chained = self._create_delivery(self.product_socks)
        socks.move_ids.move_dest_ids = chained.move_ids
        other = self._create_delivery(self.product_socks)
        operation = self._open_screen("pick")
        operation.button_skip()
        self.assertTrue(socks.move_line_ids.vertical_lift_skipped_date)

        other.priority = "1"
        self.assertTrue(socks.move_line_ids.vertical_lift_skipped_date)
        chained.priority = "1"
        self.assertFalse(socks.move_line_ids.vertical_lift_skipped_date)

    @mute_logger(SHUTTLE_LOGGER)
    def test_priority_raise_keeps_current_line_until_next_action(self):
        """The line on screen stays, the urgent one comes at the next action"""
        socks, recovery = self._create_replenishments()
        self._create_delivery(self.product_socks)
        delivery = self._create_delivery(self.product_recovery, days=1)
        operation = self._open_screen("pick")
        self.assertEqual(operation.current_move_line_id.picking_id, socks)

        delivery.priority = "1"
        self.assertEqual(operation.current_move_line_id.picking_id, socks)
        operation.select_next_move_line()
        self.assertEqual(operation.current_move_line_id.picking_id, recovery)

    @mute_logger(SHUTTLE_LOGGER)
    def test_priority_raise_then_reopen_screen(self):
        """Re-opening the screen starts from the most urgent line"""
        socks, recovery = self._create_replenishments()
        self._create_delivery(self.product_socks)
        delivery = self._create_delivery(self.product_recovery, days=1)
        operation = self._open_screen("pick")
        self.assertEqual(operation.current_move_line_id.picking_id, socks)

        delivery.priority = "1"
        operation = self._open_screen("pick")
        self.assertEqual(operation.current_move_line_id.picking_id, recovery)
        self.assertFalse(socks.move_line_ids.vertical_lift_skipped_date)
