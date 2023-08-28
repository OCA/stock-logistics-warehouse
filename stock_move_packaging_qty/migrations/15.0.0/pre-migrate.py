# Copyright 2023 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openupgradelib import openupgrade


def migrate(cr, version):
    """Use upstream column.

    In https://github.com/odoo/odoo/pull/68654, upstream added product_packaging_id.
    That feature is removed from this module and migrated there.
    """
    if openupgrade.column_exists(cr, "stock_move", "product_packaging"):
        openupgrade.rename_columns(
            cr,
            {
                "stock_move": [
                    ("product_packaging", "product_packaging_id"),
                ],
            },
        )
