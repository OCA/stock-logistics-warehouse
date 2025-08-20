# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(env):
    if openupgrade.column_exists(env.cr, "stock_move", "type_group_reservation_rate"):
        return

    fields_spec = [
        (
            "type_group_reservation_rate",
            "stock.move",
            False,
            "float",
            "float",
            "stock_picking_group_reservation_rate",
        )
    ]

    openupgrade.add_fields(env, field_spec=fields_spec)

    # Set
    query = """
        UPDATE stock_move
            SET type_group_reservation_rate = 0.0
            WHERE group_id IS NULL
            AND state IN ('draft', 'cancel')
    """
    openupgrade.logged_query(env.cr, query)

    query = """
        UPDATE stock_move
            SET type_group_reservation_rate = 100.0
            WHERE group_id IS NULL
            AND state = 'done'
    """
    openupgrade.logged_query(env.cr, query)

    # The real rate cannot be computed until the picking type group
    # has been set on the desired picking types
    # There is an action on the group to do that.
