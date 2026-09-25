# Copyright 2026 Ametras intelligence GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
"""Only the transfers a move can reach lose their completion information."""

from unittest.mock import patch

from odoo.tests import TransactionCase


class TestCompletionInfoInvalidation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.env["stock.picking.type"].search(
            [("display_completion_info", "=", True)]
        ).write({"display_completion_info": False})
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "Completion info product", "type": "consu", "is_storable": True}
        )

    def _move(self, picking=None, dest=None):
        values = {
            "name": "Completion info move",
            "product_id": self.product.id,
            "product_uom_qty": 1,
            "product_uom": self.product.uom_id.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "location_dest_id": self.customers.id,
        }
        if picking:
            values["picking_id"] = picking.id
        if dest:
            values["move_dest_ids"] = [(6, 0, dest.ids)]
        return self.env["stock.move"].create(values)

    def _picking(self, picking_type):
        return self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.customers.id,
            }
        )

    def _invalidated(self, func):
        """Return the picking ids whose completion information was dropped."""
        Picking = self.env.registry["stock.picking"]
        original = Picking.invalidate_recordset
        touched = []

        def counting(records, fnames=None, flush=True):
            if fnames and "completion_info" in fnames:
                touched.extend(records.ids)
            return original(records, fnames=fnames, flush=flush)

        with patch.object(Picking, "invalidate_recordset", counting):
            func()
        return set(touched)

    def test_nothing_is_dropped_while_no_operation_type_shows_it(self):
        """With the feature off everywhere the field is "no", so nothing ages."""
        move = self._move()
        self.assertFalse(
            self._invalidated(lambda: move.write({"state": "waiting"})),
        )

    def test_only_the_transfers_of_a_showing_type_are_dropped(self):
        """A transfer whose type hides the information is left alone."""
        self.warehouse.out_type_id.write({"display_completion_info": True})
        shown = self._picking(self.warehouse.out_type_id)
        hidden = self._picking(self.warehouse.int_type_id)
        shown_move = self._move(picking=shown)
        hidden_move = self._move(picking=hidden)
        self.assertEqual(
            self._invalidated(lambda: shown_move.write({"state": "waiting"})),
            {shown.id},
        )
        self.assertFalse(
            self._invalidated(lambda: hidden_move.write({"state": "waiting"})),
        )

    def test_a_move_reaches_the_transfers_sharing_its_destination(self):
        """The chained case: the flag that counts is the other transfer's.

        Two transfers feed the same destination. Only the first one shows the
        information. Changing a move of the second still changes what the first
        one shows, so deciding on the operation type of the move being written
        would leave a stale value behind.
        """
        self.warehouse.out_type_id.write({"display_completion_info": True})
        destination = self._picking(self.warehouse.int_type_id)
        first_dest = self._move(picking=destination)
        second_dest = self._move(picking=destination)

        shown = self._picking(self.warehouse.out_type_id)
        hidden = self._picking(self.warehouse.int_type_id)
        self._move(picking=shown, dest=first_dest)
        feeding_hidden = self._move(picking=hidden, dest=second_dest)

        self.assertIn(
            shown.id,
            self._invalidated(lambda: feeding_hidden.write({"state": "waiting"})),
            "a move of a transfer that hides the information still changes what "
            "the transfer sharing its destination shows",
        )

    def test_flag_on_archived_operation_type_still_counts(self):
        """Transfers of an archived type keep computing the field."""
        self.warehouse.out_type_id.write(
            {"display_completion_info": True, "active": False}
        )
        picking = self._picking(self.warehouse.out_type_id)
        move = self._move(picking=picking)
        self.assertEqual(
            self._invalidated(lambda: move.write({"state": "waiting"})), {picking.id}
        )

    def test_creating_and_deleting_a_flagged_operation_type_refreshes_the_lookup(self):
        """The cached list of showing operation types follows the flag."""
        PickingType = self.env["stock.picking.type"]
        self.assertFalse(PickingType._completion_info_type_ids())
        plain = PickingType.create(
            {
                "name": "Completion info plain",
                "sequence_code": "CIP",
                "code": "internal",
                "warehouse_id": self.warehouse.id,
            }
        )
        self.assertFalse(PickingType._completion_info_type_ids())
        flagged = PickingType.create(
            {
                "name": "Completion info flagged",
                "sequence_code": "CIF",
                "code": "internal",
                "warehouse_id": self.warehouse.id,
                "display_completion_info": True,
            }
        )
        self.assertEqual(PickingType._completion_info_type_ids(), (flagged.id,))
        plain.unlink()
        self.assertEqual(PickingType._completion_info_type_ids(), (flagged.id,))
        flagged.unlink()
        self.assertFalse(PickingType._completion_info_type_ids())

    def test_value_is_no_while_the_feature_is_off(self):
        picking = self._picking(self.warehouse.out_type_id)
        self.assertEqual(picking.completion_info, "no")

    def test_a_three_step_delivery_is_resolved_at_every_level(self):
        """Each transfer depends on its siblings, not on the whole chain.

        Pick, pack and ship, with two transfers feeding each level. A move of
        one pick changes what the other pick shows, because both feed the same
        pack. It does not change what the pack or the ship transfer shows:
        those depend on the moves feeding *their* destination, which are the
        pack moves. When the pack moves change state in turn, that write
        carries its own invalidation.
        """
        showing = self.warehouse.out_type_id
        showing.write({"display_completion_info": True})

        ship = self._picking(showing)
        ship_move = self._move(picking=ship)

        pack_a = self._picking(showing)
        pack_b = self._picking(showing)
        pack_a_move = self._move(picking=pack_a, dest=ship_move)
        pack_b_move = self._move(picking=pack_b, dest=ship_move)

        pick_a = self._picking(showing)
        pick_b = self._picking(showing)
        pick_a_move = self._move(picking=pick_a, dest=pack_a_move)
        self._move(picking=pick_b, dest=pack_b_move)

        # A pick move reaches its own transfer. Its sibling picks feed a
        # different pack, so they are a level apart and unaffected.
        touched = self._invalidated(lambda: pick_a_move.write({"state": "waiting"}))
        self.assertIn(pick_a.id, touched)
        self.assertNotIn(ship.id, touched)

        # A pack move reaches its own transfer and the other pack, because both
        # feed the same shipment.
        touched = self._invalidated(lambda: pack_a_move.write({"state": "waiting"}))
        self.assertIn(pack_a.id, touched)
        self.assertIn(pack_b.id, touched)

    def test_the_cached_value_matches_a_fresh_one(self):
        """A cached value must equal what a recomputation produces.

        This is the point of the invalidation: after a state change in the
        transfer sharing its destination, what the other one still holds has to
        be what it would compute now.
        """
        showing = self.warehouse.out_type_id
        showing.write({"display_completion_info": True})
        ship = self._picking(showing)
        ship_move = self._move(picking=ship)
        pack_a = self._picking(showing)
        pack_b = self._picking(showing)
        self._move(picking=pack_a, dest=ship_move)
        pack_b_move = self._move(picking=pack_b, dest=ship_move)

        # Fill the cache, then change the sibling.
        self.assertTrue(pack_a.completion_info)
        pack_b_move.write({"state": "done"})

        cached = pack_a.completion_info
        pack_a.invalidate_recordset(["completion_info"])
        self.assertEqual(
            cached,
            pack_a.completion_info,
            "the value held for one transfer no longer matches what it computes "
            "after a state change in the transfer sharing its destination",
        )
