# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tools.sql import column_exists


def migrate(cr, version):
    if not version:
        return
    if column_exists(cr, "stock_warehouse", "orderpoint_on_workday"):
        # Store ``orderpoint_on_workday`` in a temporary column to be used in the post-mig
        # script to set default values for ``orderpoint_on_workday_policy``
        cr.execute(
            """
            ALTER TABLE stock_warehouse
            ADD COLUMN IF NOT EXISTS orderpoint_on_workday_tmp BOOLEAN DEFAULT false
            """
        )
        cr.execute(
            """
            UPDATE stock_warehouse
            SET orderpoint_on_workday_tmp = true
            WHERE orderpoint_on_workday
            """
        )
