# Copyright 2020 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade

column_renames = {
    "stock_inventory": [
        ("location_id", None),
        ("product_id", None),
        ("category_id", None),
        ("lot_id", None),
    ]
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, column_renames)
