# Copyright 2026 FactorLibre - Álvaro Marcos
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""The assign sweep works in batches and survives a bad reservation.

Before batching, the sweep was a bare loop in a single transaction: a
single failing reservation aborted everything, so none of the pending
reservations ended up assigned -- not even the ones already processed --
and there was no retry until the next run.
"""
from unittest.mock import patch

from odoo.tests import Form, common


class TestAssignSweep(common.TransactionCase):
    def setUp(self):
        super().setUp()
        warehouse_form = Form(self.env["stock.warehouse"])
        warehouse_form.name = "Sweep warehouse"
        warehouse_form.code = "SWP"
        self.warehouse = warehouse_form.save()
        product_form = Form(self.env["product.product"])
        product_form.name = "Sweep Product"
        product_form.detailed_type = "product"
        self.product = product_form.save()
        self.reservation_model = self.env["stock.reservation"]

    def _reservations(self, count, qty=1.0):
        """Reservations waiting for stock, which is what the sweep looks for.

        A freshly created reservation is still a draft move, and the sweep
        only looks at ``confirmed`` / ``waiting`` / ``partially_available``
        ones. Reserving them while there is no stock leaves them exactly
        there: confirmed, waiting for goods that have not arrived.
        """
        reservations = self.reservation_model.create(
            [
                {
                    "product_id": self.product.id,
                    "product_uom_qty": qty,
                    "product_uom": self.product.uom_id.id,
                    "name": "sweep %s" % index,
                    "location_id": self.warehouse.lot_stock_id.id,
                }
                for index in range(count)
            ]
        )
        reservations.reserve()
        self.assertEqual(set(reservations.mapped("state")), {"confirmed"})
        return reservations

    def _add_stock(self, qty):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.warehouse.lot_stock_id, qty
        )

    def _pending_ids(self):
        """The reservations the sweep will pick up, in its own order."""
        return self.reservation_model.search(
            self.reservation_model._get_reservations_to_assign_domain()
        ).ids

    def test_01_the_sweep_assigns_the_pending_reservations(self):
        reservations = self._reservations(3)
        self._add_stock(500.0)
        self.reservation_model.assign_waiting_confirmed_reserve_moves()
        for reservation in reservations:
            self.assertGreater(reservation.move_id.reserved_availability, 0.0)

    def test_02_a_failing_batch_is_skipped_without_raising(self):
        """The batch is lost, but the sweep returns normally."""
        reservations = self._reservations(3)
        self._add_stock(500.0)

        def failing_reserve(records):
            raise ValueError("bad data in this batch")

        with patch.object(type(reservations), "reserve", failing_reserve):
            self.assertTrue(
                self.reservation_model.assign_waiting_confirmed_reserve_moves()
            )
        for reservation in reservations:
            self.assertEqual(reservation.move_id.reserved_availability, 0.0)

    def test_03_a_failing_batch_does_not_stop_the_next_one(self):
        """51 reservations make two batches with the default size of 50: the
        first one fails and the second is still assigned.
        """
        reservations = self._reservations(51)
        self._add_stock(500.0)
        # Same domain and same order the sweep uses, so the batches under
        # test are the batches it will really build.
        pending = self._pending_ids()
        self.assertEqual(len(pending), 51)
        first_batch = set(pending[:50])
        last = self.reservation_model.browse(pending[50])
        original_reserve = type(reservations).reserve

        def selective_reserve(records):
            if set(records.ids) & first_batch:
                raise ValueError("bad data in the first batch")
            return original_reserve(records)

        with patch.object(type(reservations), "reserve", selective_reserve):
            self.reservation_model.assign_waiting_confirmed_reserve_moves()

        for reservation in self.reservation_model.browse(sorted(first_batch)):
            self.assertEqual(reservation.move_id.reserved_availability, 0.0)
        self.assertGreater(last.move_id.reserved_availability, 0.0)

    def test_04_batch_size_comes_from_the_system_parameter(self):
        """With the parameter set to 2, five reservations make three
        batches of 2, 2 and 1.
        """
        reservations = self._reservations(5)
        self._add_stock(500.0)
        original_reserve = type(reservations).reserve
        sizes = []

        def counting_reserve(records):
            sizes.append(len(records))
            return original_reserve(records)

        self.env["ir.config_parameter"].sudo().set_param(
            "stock_reserve.assign_batch_size", "2"
        )
        with patch.object(type(reservations), "reserve", counting_reserve):
            self.reservation_model.assign_waiting_confirmed_reserve_moves()
        self.assertEqual(sizes, [2, 2, 1])

    def test_05_default_batch_size_is_fifty(self):
        """Parameter absent: the five of them fit in a single batch."""
        reservations = self._reservations(5)
        self._add_stock(500.0)
        self.assertFalse(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_reserve.assign_batch_size")
        )
        original_reserve = type(reservations).reserve
        sizes = []

        def counting_reserve(records):
            sizes.append(len(records))
            return original_reserve(records)

        with patch.object(type(reservations), "reserve", counting_reserve):
            self.reservation_model.assign_waiting_confirmed_reserve_moves()
        self.assertEqual(sizes, [5])

    def test_06_empty_sweep_is_a_no_op(self):
        self.assertFalse(self._pending_ids())
        self.assertTrue(self.reservation_model.assign_waiting_confirmed_reserve_moves())
