# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.osv.expression import AND

from odoo.addons.base.tests.common import BaseCommon

from ..models.stock_location import PENDING_MOVE_DOMAIN


class TestLocationPendingMove(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock = cls.env.ref("stock.stock_location_stock")

    def test_location_pending_move(self):
        # Check that the action domain is well filled with pending moves ids.
        domain = AND(
            [
                [
                    "|",
                    ("location_id", "=", self.stock.id),
                    ("location_dest_id", "=", self.stock.id),
                ],
                PENDING_MOVE_DOMAIN,
            ]
        )
        moves = self.env["stock.move"].search(domain)
        action = self.stock.action_show_pending_stock_moves()
        self.assertDictContainsSubset({"domain": [("id", "in", moves.ids)]}, action)

    def test_location_pending_move_line(self):
        # Check that the action domain is well filled with pending move lines ids.
        domain = AND(
            [
                [
                    "|",
                    ("location_id", "=", self.stock.id),
                    ("location_dest_id", "=", self.stock.id),
                ],
                PENDING_MOVE_DOMAIN,
            ]
        )
        move_lines = self.env["stock.move.line"].search(domain)
        action = self.stock.action_show_pending_stock_move_lines()
        self.assertDictContainsSubset(
            {"domain": [("id", "in", move_lines.ids)]}, action
        )
