# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Move the template's second unit for inventory to its variants.

    The template field is now a mirror of its variants, and quants read the
    variant's. Pre-migration, so that the new stored quant unit is computed
    from the variants once they carry it.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_product pp
        SET stock_secondary_uom_id = pt.stock_secondary_uom_id
        FROM product_template pt
        WHERE pp.product_tmpl_id = pt.id
            AND pp.stock_secondary_uom_id IS NULL
            AND pt.stock_secondary_uom_id IS NOT NULL
        """,
    )
    # The stored template field is not recomputed on upgrade, so align it with
    # the variants: their value when they all share one, empty otherwise
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template pt
        SET stock_secondary_uom_id = sub.uom_id
        FROM (
            SELECT product_tmpl_id,
                CASE WHEN count(DISTINCT stock_secondary_uom_id) = 1
                    THEN min(stock_secondary_uom_id) END AS uom_id
            FROM product_product
            WHERE active
            GROUP BY product_tmpl_id
        ) sub
        WHERE sub.product_tmpl_id = pt.id
            AND pt.stock_secondary_uom_id IS DISTINCT FROM sub.uom_id
        """,
    )
