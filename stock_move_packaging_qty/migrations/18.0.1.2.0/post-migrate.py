# Copyright 2026 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tools import sql


def migrate(cr, version):
    """Activate Picking Type Automatic Done Packaging Calculation."""
    if not sql.column_exists(
        cr, "stock_picking_type", "automatic_done_packaging_calculation"
    ):
        sql.create_column(
            cr,
            "stock_picking_type",
            "automatic_done_packaging_calculation",
            "boolean",
            comment="Automatically Calculate Done Packaging Quantity",
        )
    cr.execute(
        "UPDATE stock_picking_type SET automatic_done_packaging_calculation = True"
    )
