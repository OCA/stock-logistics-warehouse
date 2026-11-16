# Copyright 2026 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "stock_rule", "auto_create_group"):
        openupgrade.rename_fields(
            env,
            [
                (
                    "stock.rule",
                    "stock_rule",
                    "auto_create_group",
                    "auto_create_reference",
                )
            ],
        )
