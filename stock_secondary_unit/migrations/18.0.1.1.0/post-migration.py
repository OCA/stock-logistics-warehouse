# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo.tools import float_compare


@openupgrade.migrate()
def migrate(env, version):
    """Fix the returns whose secondary quantity was left inconsistent by ``copy``."""
    precision = env["decimal.precision"].precision_get("Product Unit of Measure")
    moves = env["stock.move"].search(
        [
            ("origin_returned_move_id", "!=", False),
            ("secondary_uom_id", "!=", False),
            ("secondary_uom_id.dependency_type", "=", "dependent"),
            ("state", "!=", "cancel"),
        ]
    )
    updates = {}
    for move in moves:
        expected = move._convert_qty_to_secondary_uom(move.product_uom_qty)
        if float_compare(move.secondary_uom_qty, expected, precision) != 0:
            updates.setdefault(expected, []).append(move.id)
    for qty, move_ids in updates.items():
        openupgrade.logged_query(
            env.cr,
            "UPDATE stock_move SET secondary_uom_qty = %s WHERE id IN %s",
            (qty, tuple(move_ids)),
        )
