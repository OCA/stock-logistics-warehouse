# Copyright 2023 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_stock_quant_reason(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line sml
        SET reason = sil.reason
        FROM stock_inventory_line sil
        JOIN stock_inventory si ON sil.inventory_id = si.id
        JOIN stock_location sl ON sil.location_id = sl.id
        JOIN stock_move sm ON sm.inventory_id = si.id
        WHERE sil.reason IS NOT NULL AND sml.move_id = sm.id
            AND sml.location_id = sl.id
            AND sl.usage in ('internal', 'transit')
            AND si.state = 'done' AND sml.product_id = sil.product_id
            AND ((sil.prod_lot_id IS NULL AND sml.lot_id IS NULL) OR (
                sil.prod_lot_id = sml.lot_id))
            AND COALESCE(sml.date, sm.date) = COALESCE(
                sil.inventory_date, si.date)""",
    )


def fill_stock_move_line_preset_reason_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line sml
        SET preset_reason_id = sm.preset_reason_id
        FROM stock_move sm
        WHERE sml.move_id = sm.id AND sm.preset_reason_id IS NOT NULL""",
    )


def fill_stock_move_line_reason(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line sml
        SET reason = COALESCE(sml.reason, sqr.name)
        FROM stock_quant_reason sqr
        WHERE sml.preset_reason_id = sqr.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_stock_quant_reason(env)
    fill_stock_move_line_preset_reason_id(env)
    fill_stock_move_line_reason(env)
