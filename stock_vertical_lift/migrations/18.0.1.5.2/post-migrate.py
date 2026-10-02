# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """Give a skip date to the lines skipped with the former boolean.

    Only the lines still proposed by the shuttle matter: the flag is
    meaningless on done or cancelled lines. The old column is left in place.
    """
    cr.execute(
        """
        UPDATE stock_move_line
        SET vertical_lift_skipped_date = COALESCE(write_date, now() AT TIME ZONE 'UTC')
        WHERE vertical_lift_skipped
          AND vertical_lift_skipped_date IS NULL
          AND state IN ('assigned', 'partially_available')
        """
    )
