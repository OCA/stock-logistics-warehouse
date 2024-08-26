# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tools.sql import column_exists


def migrate(cr, version):
    if not version:
        return
    if column_exists(cr, "stock_warehouse", "orderpoint_on_workday_tmp"):
        # Fill ``orderpoint_on_workday_policy`` with a default value where needed, then
        # drop the temporary column
        cr.execute(
            """
            UPDATE stock_warehouse
            SET orderpoint_on_workday_policy = 'skip_to_first_workday'
            WHERE orderpoint_on_workday_tmp
            """
        )
        cr.execute(
            """
            ALTER TABLE stock_warehouse
            DROP COLUMN orderpoint_on_workday_tmp
            """
        )
