# Copyright 2026 Tecnativa - Juan Carlos Oñate
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    products = env["product.product"].with_context(active_test=False)
    # The template value never reached its variants, so variants without their
    # own value inherit it from the template, archived ones included.
    variants = products.search(
        [
            ("stock_secondary_uom_id", "=", False),
            ("product_tmpl_id.stock_secondary_uom_id", "!=", False),
        ]
    )
    for secondary_uom, uom_variants in variants.grouped(
        lambda variant: variant.product_tmpl_id.stock_secondary_uom_id
    ).items():
        uom_variants.stock_secondary_uom_id = secondary_uom
    # Variants that already had their own value also rule the template now.
    # Queue the recomputation instead of calling the compute method: assigning
    # outside the recomputation runs the inverse and overwrites the variants.
    templates = products.search(
        [("stock_secondary_uom_id", "!=", False)]
    ).product_tmpl_id
    env.add_to_compute(templates._fields["stock_secondary_uom_id"], templates)
    templates.flush_recordset(["stock_secondary_uom_id"])
