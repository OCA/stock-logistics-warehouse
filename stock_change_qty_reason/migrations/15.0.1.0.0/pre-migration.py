# Copyright 2023 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_required_reason(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_quant_reason sqr
        SET name = '???'
        WHERE name IS NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(
        env.cr, [("stock_inventory_line_reason", "stock_quant_reason")]
    )
    openupgrade.rename_models(
        env.cr, [("stock.inventory.line.reason", "stock.quant.reason")]
    )
    fill_required_reason(env)
