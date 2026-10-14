# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Create and backfill secondary_uom_qty_done via SQL.

    Pre-migration, not post: creating the column here means Odoo's own
    schema sync finds it already in place and skips the automatic
    per-record Python recompute it would otherwise trigger for every
    existing stock.move.
    """
    openupgrade.add_columns(
        env,
        [("stock.move", "secondary_uom_qty_done", "float")],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET secondary_uom_qty_done = sub.total
        FROM (
            SELECT move_id, SUM(secondary_uom_qty) AS total
            FROM stock_move_line
            GROUP BY move_id
        ) sub
        WHERE sub.move_id = sm.id
        """,
    )
