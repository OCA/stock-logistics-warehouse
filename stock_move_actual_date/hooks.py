# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def pre_init_hook(cr):
    if not openupgrade.column_exists(cr, "stock_move", "actual_date"):
        cr.execute(
            """
            ALTER TABLE stock_move
            ADD COLUMN actual_date DATE;
            UPDATE stock_move
            SET actual_date = DATE(date);
            """
        )
        cr.execute(
            """
            ALTER TABLE stock_move_line
            ADD COLUMN actual_date DATE;
            UPDATE stock_move_line
            SET actual_date = DATE(date);
            """
        )
