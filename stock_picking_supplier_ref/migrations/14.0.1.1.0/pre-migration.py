# Copyright 2022 Studio73 - Carlos Reyes <carlos@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade

field_renames = [
    (
        "stock.picking",
        "stock_picking",
        "reference",
        "supplier_reference",
    )
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "stock_picking", "reference"):
        openupgrade.rename_fields(env, field_renames)
