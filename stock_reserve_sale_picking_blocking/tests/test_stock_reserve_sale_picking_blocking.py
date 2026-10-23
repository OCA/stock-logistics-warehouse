# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.fields import Command
from odoo.tests.common import Form, TransactionCase


class TestStockReserveSalePickingBlocking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.SaleStockReserve = cls.env["sale.stock.reserve"]
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )
        cls.block_reason = cls.env["sale.delivery.block.reason"].create(
            {"name": "Test Block"}
        )
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.warehouse.lot_stock_id, 10.0
        )
        cls.env.company.sale_stock_reservation_policy = "always"

    @classmethod
    def _create_sale_order(cls, quantity, **kwargs):
        vals = {
            "partner_id": cls.partner.id,
            "warehouse_id": cls.warehouse.id,
            "order_line": [
                Command.create(
                    {"product_id": cls.product.id, "product_uom_qty": quantity}
                )
            ],
        }
        vals.update(kwargs)
        return cls.SaleOrder.create(vals)

    def _reserve(self, order):
        wizard_form = Form(
            self.SaleStockReserve.with_context(
                active_model="sale.order", active_id=order.id, active_ids=order.ids
            )
        )
        wizard_form.location_id = self.warehouse.lot_stock_id
        wizard_form.save().button_reserve()
        return order.stock_reservation_ids

    def test_confirm_blocked_order_keeps_reservation(self):
        order = self._create_sale_order(4.0, delivery_block_id=self.block_reason.id)
        reservation = self._reserve(order)
        self.assertEqual(reservation.state, "assigned")
        order.action_confirm()
        self.assertEqual(order.state, "sale")
        self.assertFalse(order.picking_ids)
        self.assertEqual(reservation.state, "assigned")
        self.assertEqual(order.order_line.reservation_ids, reservation)
        self.assertTrue(order.has_stock_reservation)

    def test_confirm_unblocked_order_releases_reservation(self):
        blocked_order = self._create_sale_order(
            4.0, delivery_block_id=self.block_reason.id
        )
        unblocked_order = self._create_sale_order(6.0)
        blocked_reservation = self._reserve(blocked_order)
        unblocked_reservation = self._reserve(unblocked_order)
        (blocked_order | unblocked_order).action_confirm()
        self.assertEqual(blocked_reservation.state, "assigned")
        self.assertFalse(blocked_order.picking_ids)
        self.assertEqual(unblocked_reservation.state, "cancel")
        self.assertFalse(unblocked_order.order_line.reservation_ids)
        self.assertEqual(unblocked_order.picking_ids.state, "assigned")

    def test_remove_delivery_block_releases_reservation(self):
        blocked_order = self._create_sale_order(
            10.0, delivery_block_id=self.block_reason.id
        )
        reservation = self._reserve(blocked_order)
        blocked_order.action_confirm()
        other_order = self._create_sale_order(5.0)
        other_order.action_confirm()
        self.assertEqual(other_order.picking_ids.state, "confirmed")
        blocked_order.action_remove_delivery_block()
        self.assertFalse(blocked_order.delivery_block_id)
        self.assertEqual(reservation.state, "cancel")
        self.assertFalse(blocked_order.order_line.reservation_ids)
        self.assertEqual(blocked_order.picking_ids.state, "assigned")
        self.assertEqual(other_order.picking_ids.state, "confirmed")

    def test_cancel_blocked_order_releases_reservation(self):
        order = self._create_sale_order(4.0, delivery_block_id=self.block_reason.id)
        reservation = self._reserve(order)
        order.action_confirm()
        action = order.action_cancel()
        self.assertEqual(action["res_model"], "sale.order.cancel")
        self.assertEqual(reservation.state, "assigned")
        wizard = (
            self.env["sale.order.cancel"]
            .with_context(**action["context"])
            .create({"order_id": order.id})
        )
        wizard.action_cancel()
        self.assertEqual(order.state, "cancel")
        self.assertEqual(reservation.state, "cancel")

    def test_release_blocked_order_reservation_manually(self):
        order = self._create_sale_order(4.0, delivery_block_id=self.block_reason.id)
        reservation = self._reserve(order)
        order.action_confirm()
        action = order.action_open_release_reservation_wizard()
        self.env["sale.stock.reserve.release"].browse(action["res_id"]).button_release()
        self.assertEqual(reservation.state, "cancel")
        self.assertFalse(order.has_stock_reservation)
        self.assertTrue(order.delivery_block_id)
        self.assertFalse(order.picking_ids)
