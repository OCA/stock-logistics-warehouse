# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tools.sql import column_exists, table_exists


def pre_init_hook(cr):
    if not column_exists(cr, "stock_move", "area_reserved_availability"):
        cr.execute(
            """
                ALTER TABLE "stock_move"
                ADD COLUMN "area_reserved_availability" double precision DEFAULT 0
            """
        )
        cr.execute(
            """
        ALTER TABLE "stock_move" ALTER COLUMN "area_reserved_availability" DROP DEFAULT
        """
        )

    if not table_exists(cr, "stock_move_stock_reserve_area_rel"):
        cr.execute(
            """
        CREATE TABLE stock_move_stock_reserve_area_rel
        (stock_move_id INTEGER, stock_reserve_area_id INTEGER);
        """
        )
